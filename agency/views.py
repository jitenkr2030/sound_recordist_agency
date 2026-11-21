import csv, json, os, sqlite3, tempfile, zipfile
from datetime import date
from decimal import Decimal
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from . import models
from .forms import LeadForm, AudioAssetForm

MODULES = {
 "clients": ("Clients", models.Client, ["name","company","email","phone","client_type"]),
 "professionals": ("Sound Recordists", models.Professional, ["name","category","phone","experience_years","day_rate","verified"]),
 "freelancers": ("Freelancers", models.Freelancer, ["name","skill","phone","rate","available"]),
 "projects": ("Projects", models.Project, ["code","name","client","category","status","start_date","end_date"]),
 "bookings": ("Bookings", models.Booking, ["client","project","professional","start_at","end_at","status","amount"]),
 "equipment": ("Equipment", models.Equipment, ["asset_tag","name","category","brand","serial_number","status"]),
 "allocations": ("Equipment Allocations", models.EquipmentAllocation, ["equipment","project","issued_to","issued_at","due_at","returned_at"]),
 "studios": ("Studios", models.Studio, ["name","room","capacity","hourly_rate","active"]),
 "studio-sessions": ("Studio Sessions", models.StudioSession, ["studio","client","project","start_at","end_at","status"]),
 "recording-sessions": ("Recording Sessions", models.RecordingSession, ["project","recordist","session_date","scene_number","take_number","audio_format","take_quality"]),
 "audio-assets": ("Audio Assets", models.AudioAsset, ["project","title","version","is_client_visible","approved"]),
 "services": ("Services", models.Service, ["name","unit","base_rate","gst_rate","active"]),
 "quotations": ("Quotations", models.Quotation, ["number","client","project","issue_date","subtotal","gst_amount","total","status"]),
 "contracts": ("Contracts", models.Contract, ["number","client","project","title","start_date","end_date","status"]),
 "invoices": ("Invoices", models.Invoice, ["number","client","project","invoice_date","due_date","subtotal","gst_amount","total","amount_paid","status"]),
 "payments": ("Payments", models.Payment, ["receipt_number","client","invoice","date","amount","method","reference"]),
 "expenses": ("Expenses", models.Expense, ["date","category","description","amount","project","vendor"]),
 "leads": ("Leads", models.Lead, ["name","organisation","email","phone","source","status"]),
 "tasks": ("Tasks", models.Task, ["title","project","assigned_to","due_date","priority","status"]),
 "documents": ("Documents", models.Document, ["title","category","project","client","uploaded_by"]),
 "reviews": ("Reviews", models.Review, ["client","project","rating","is_public"]),
 "branches": ("Branches", models.Branch, ["name","code","phone","email","gstin","is_active"]),
 "notifications": ("Notifications", models.Notification, ["title","message","read","created_at"]),
 "audit": ("Audit Logs", models.AuditLog, ["user","action","model_name","object_id","created_at"]),
}
PORTALS = {
 "admin": ("Agency Admin Portal", ["All modules, users, settings, reports and backups"]),
 "recordist": ("Sound Recordist Portal", ["My assignments", "Recording sessions", "My profile", "Audio uploads"]),
 "client": ("Client Portal", ["My projects", "My bookings", "Invoices and payments", "Approved audio deliveries"]),
 "freelancer": ("Freelancer Portal", ["My assignments", "Availability", "Timesheets and payments"]),
 "equipment": ("Equipment Manager Portal", ["Equipment inventory", "Allocations", "Returns", "Maintenance status"]),
}
ROLE_PORTALS = {"ADMIN":"admin","MANAGER":"admin","RECORDIST":"recordist","CLIENT":"client","FREELANCER":"freelancer","EQUIPMENT":"equipment","ACCOUNTANT":"admin","HR":"admin"}
def role(user):
    try: return user.agency_profile.role
    except Exception: return "ADMIN" if user.is_superuser else "CLIENT"
def can_manage(user):
    return user.is_superuser or role(user) in ["ADMIN","MANAGER","ACCOUNTANT","EQUIPMENT","HR"]
def home(request):
    return render(request,"agency/home.html",{"professionals":models.Professional.objects.filter(active=True)[:6],"services":models.Service.objects.filter(active=True)[:6]})
def contact(request):
    if request.method=="POST":
        form=LeadForm(request.POST)
        if form.is_valid(): form.save(); messages.success(request,"Thank you. Your enquiry has been received."); return redirect("home")
    else: form=LeadForm()
    return render(request,"agency/contact.html",{"form":form})
def public_lead(request):
    if request.method=="POST":
        form=LeadForm(request.POST)
        if form.is_valid(): form.save(); messages.success(request,"Enquiry submitted."); return redirect("home")
    return redirect("contact")
def login_view(request):
    if request.method=="POST":
        user=authenticate(request,username=request.POST.get("username"),password=request.POST.get("password"))
        if user:
            login(request,user); return redirect("dashboard")
        messages.error(request,"Invalid username or password.")
    return render(request,"registration/login.html")
@login_required
def logout_view(request):
    logout(request); return redirect("home")
@login_required
def dashboard(request):
    ctx={
      "counts": {label: model.objects.count() for slug,(label,model,cols) in MODULES.items()},
      "projects": models.Project.objects.select_related("client").order_by("-created_at")[:8],
      "bookings": models.Booking.objects.select_related("client").order_by("start_at")[:8],
      "revenue": models.Payment.objects.aggregate(v=Sum("amount"))["v"] or 0,
      "expenses": models.Expense.objects.aggregate(v=Sum("amount"))["v"] or 0,
      "role":role(request.user), "portal_slug":ROLE_PORTALS.get(role(request.user),"client"), "modules":MODULES,
    }
    return render(request,"agency/dashboard.html",ctx)
@login_required
def portal(request,portal):
    expected=ROLE_PORTALS.get(role(request.user),"client")
    if not (request.user.is_superuser or portal == expected):
        return HttpResponseForbidden("You do not have access to this portal.")
    return render(request,"agency/portal.html",{"portal":PORTALS.get(portal,PORTALS["client"]),"portal_key":portal})
def _module(slug):
    return MODULES.get(slug)
@login_required
def module_list(request,slug):
    info=_module(slug)
    if not info: return redirect("dashboard")
    label,model,columns=info
    qs=model.objects.all().order_by("-pk")
    # Client-facing users only see their own linked client/project records.
    if role(request.user)=="CLIENT" and not request.user.is_superuser:
        try:
            client=request.user.client_record
            if model is models.Client: qs=qs.filter(pk=client.pk)
            elif model is models.Project: qs=qs.filter(client=client)
            elif model is models.Booking: qs=qs.filter(client=client)
            elif model is models.Invoice: qs=qs.filter(client=client)
            elif model is models.Payment: qs=qs.filter(client=client)
            elif model is models.AudioAsset: qs=qs.filter(project__client=client,is_client_visible=True)
            else: qs=model.objects.none()
        except Exception: qs=model.objects.none()
    return render(request,"agency/module_list.html",{"label":label,"slug":slug,"objects":qs[:250],"columns":columns,"can_manage":can_manage(request.user),"model":model})
@login_required
def _save_model(request,slug,pk=None):
    info=_module(slug)
    if not info: return redirect("dashboard")
    if not can_manage(request.user): return HttpResponseForbidden("Permission denied.")
    label,model,columns=info
    instance=get_object_or_404(model,pk=pk) if pk else None
    fields=[f.name for f in model._meta.fields if f.name not in ["id","created_at","updated_at"]]
    if request.method=="POST":
        from django.forms import modelform_factory
        Form=modelform_factory(model,fields=fields)
        form=Form(request.POST,request.FILES,instance=instance)
        if form.is_valid():
            obj=form.save()
            models.AuditLog.objects.create(user=request.user,action="SAVE",model_name=model.__name__,object_id=str(obj.pk),detail=f"{label} saved")
            messages.success(request,f"{label[:-1] if label.endswith('s') else label} saved successfully.")
            return redirect("module_list",slug=slug)
    else:
        from django.forms import modelform_factory
        Form=modelform_factory(model,fields=fields)
        form=Form(instance=instance)
    return render(request,"agency/module_form.html",{"form":form,"label":label,"slug":slug,"instance":instance})
@login_required
def module_create(request,slug): return _save_model(request,slug)
@login_required
def module_edit(request,slug,pk): return _save_model(request,slug,pk)
@login_required
@require_POST
def module_delete(request,slug,pk):
    if not can_manage(request.user): return HttpResponseForbidden("Permission denied.")
    info=_module(slug)
    if info:
        obj=get_object_or_404(info[1],pk=pk)
        models.AuditLog.objects.create(user=request.user,action="DELETE",model_name=info[1].__name__,object_id=str(pk))
        obj.delete()
    return redirect("module_list",slug=slug)
@login_required
def reports(request):
    return render(request,"agency/reports.html",{
      "payments":models.Payment.objects.aggregate(v=Sum("amount"))["v"] or 0,
      "expenses":models.Expense.objects.aggregate(v=Sum("amount"))["v"] or 0,
      "invoice_total":models.Invoice.objects.aggregate(v=Sum("total"))["v"] or 0,
      "outstanding":sum((i.total-i.amount_paid for i in models.Invoice.objects.exclude(status="CANCELLED")),Decimal("0")),
      "projects":models.Project.objects.values("status").annotate(n=Count("id")), "modules":[(k,v[0]) for k,v in MODULES.items()],
    })
@login_required
def export_csv(request):
    if not can_manage(request.user): return HttpResponseForbidden()
    slug=request.GET.get("module","projects")
    info=_module(slug)
    if not info: return redirect("reports")
    label,model,columns=info
    response=HttpResponse(content_type="text/csv")
    response["Content-Disposition"]=f'attachment; filename="{slug}.csv"'
    writer=csv.writer(response); writer.writerow(columns)
    for obj in model.objects.all().iterator():
        writer.writerow([str(getattr(obj,c,"")) for c in columns])
    return response
@login_required
def insights(request):
    revenue=models.Payment.objects.aggregate(v=Sum("amount"))["v"] or Decimal("0")
    costs=models.Expense.objects.aggregate(v=Sum("amount"))["v"] or Decimal("0")
    pending=models.Invoice.objects.exclude(status__in=["PAID","CANCELLED"]).count()
    insights=[
      f"Recorded receipts total ₹{revenue:,.2f}.",
      f"Recorded expenses total ₹{costs:,.2f}.",
      f"Indicative cash surplus before other adjustments: ₹{revenue-costs:,.2f}.",
      f"{pending} invoices need collection follow-up.",
      f"{models.Equipment.objects.filter(status='MAINTENANCE').count()} equipment assets are marked under maintenance.",
      f"{models.Project.objects.filter(status='IN_PROGRESS').count()} projects are currently in progress.",
    ]
    return render(request,"agency/insights.html",{"insights":insights,"note":"These are rule-based management insights, not an external generative-AI service or certified financial advice."})
@login_required
def backup_page(request):
    if not (request.user.is_superuser or role(request.user)=="ADMIN"): return HttpResponseForbidden()
    return render(request,"agency/backup.html")
@login_required
def backup_download(request):
    if not (request.user.is_superuser or role(request.user)=="ADMIN"): return HttpResponseForbidden()
    tmp=tempfile.NamedTemporaryFile(suffix=".zip",delete=False); tmp.close()
    with zipfile.ZipFile(tmp.name,"w",zipfile.ZIP_DEFLATED) as z:
        db=settings.DATABASES["default"]
        if db["ENGINE"].endswith("sqlite3") and os.path.exists(db["NAME"]): z.write(db["NAME"],"db.sqlite3")
        for root,dirs,files_ in os.walk(settings.MEDIA_ROOT):
            for f in files_:
                p=os.path.join(root,f); z.write(p,os.path.relpath(p,settings.BASE_DIR))
        z.writestr("BACKUP_INFO.txt","Database and media backup. Store securely. Restore manually after verifying files.")
    models.AuditLog.objects.create(user=request.user,action="BACKUP",model_name="System")
    return FileResponse(open(tmp.name,"rb"),as_attachment=True,filename="sound_agency_backup.zip")
@login_required
def audio_upload(request):
    if not can_manage(request.user) and role(request.user)!="RECORDIST": return HttpResponseForbidden()
    if request.method=="POST":
        form=AudioAssetForm(request.POST,request.FILES)
        if form.is_valid():
            obj=form.save(commit=False); obj.uploaded_by=request.user; obj.save()
            messages.success(request,"Audio file uploaded.")
            return redirect("audio_list")
    else: form=AudioAssetForm()
    return render(request,"agency/module_form.html",{"form":form,"label":"Upload Audio Asset","slug":"audio-assets"})
@login_required
def audio_list(request):
    qs=models.AudioAsset.objects.select_related("project")
    if role(request.user)=="CLIENT":
        try: qs=qs.filter(project__client=request.user.client_record,is_client_visible=True)
        except Exception: qs=qs.none()
    return render(request,"agency/audio_list.html",{"objects":qs})
