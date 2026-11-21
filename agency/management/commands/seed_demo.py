from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from agency.models import *
class Command(BaseCommand):
    help="Create demo agency records and portal users. Demo passwords must be changed."
    def handle(self,*args,**kwargs):
        branch,_=Branch.objects.get_or_create(code="DEL-01",defaults={"name":"Delhi Main Branch","address":"Delhi, India"})
        admin,_=User.objects.get_or_create(username="admin",defaults={"email":"admin@example.com","is_staff":True,"is_superuser":True})
        if not admin.has_usable_password(): admin.set_password("Admin@12345"); admin.save()
        UserProfile.objects.get_or_create(user=admin,defaults={"role":"ADMIN","branch":branch})
        for username,role in [("manager","MANAGER"),("recordist","RECORDIST"),("client","CLIENT"),("freelancer","FREELANCER"),("equipment","EQUIPMENT"),("accountant","ACCOUNTANT")]:
            u,_=User.objects.get_or_create(username=username,defaults={"email":f"{username}@example.com"})
            if not u.has_usable_password(): u.set_password("Demo@12345"); u.save()
            UserProfile.objects.get_or_create(user=u,defaults={"role":role,"branch":branch})
        client,_=Client.objects.get_or_create(name="Demo Production House",defaults={"company":"Demo Production House","email":"client@example.com","branch":branch})
        client.account_user=User.objects.get(username="client"); client.save()
        prof,_=Professional.objects.get_or_create(name="Aarav Sharma",defaults={"category":"PRODUCTION_SOUND_RECORDIST","experience_years":8,"day_rate":8500,"verified":True,"branch":branch,"user":User.objects.get(username="recordist")})
        Service.objects.get_or_create(name="Location Sound Recording",defaults={"unit":"day","base_rate":12000,"gst_rate":18})
        Service.objects.get_or_create(name="Studio Recording",defaults={"unit":"hour","base_rate":2500,"gst_rate":18})
        Project.objects.get_or_create(code="SRA-0001",defaults={"name":"Demo Documentary","client":client,"category":"DOCUMENTARY","status":"IN_PROGRESS","manager":admin,"branch":branch})
        Equipment.objects.get_or_create(asset_tag="MIC-001",defaults={"name":"Shotgun Microphone","category":"Microphone","brand":"Demo Audio","status":"AVAILABLE","branch":branch})
        Studio.objects.get_or_create(name="Main Recording Studio",defaults={"room":"Studio A","capacity":4,"hourly_rate":2500})
        self.stdout.write(self.style.SUCCESS("Demo data created. Login admin/Admin@12345; manager, recordist, client, freelancer, equipment, accountant / Demo@12345"))
