from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Branch(TimeStamped):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class UserProfile(TimeStamped):
    ROLES = [(x,x.replace("_"," ").title()) for x in ["ADMIN","MANAGER","RECORDIST","CLIENT","FREELANCER","EQUIPMENT","ACCOUNTANT","HR"]]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="agency_profile")
    role = models.CharField(max_length=20, choices=ROLES, default="CLIENT")
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=160, blank=True)
    def __str__(self): return f"{self.user.username} ({self.role})"

class Client(TimeStamped):
    TYPES = [("INDIVIDUAL","Individual"),("COMPANY","Company"),("PRODUCTION","Production House"),("GOVERNMENT","Government"),("AGENCY","Agency")]
    name = models.CharField(max_length=160)
    client_type = models.CharField(max_length=20, choices=TYPES, default="COMPANY")
    company = models.CharField(max_length=160, blank=True)
    contact_person = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    pan = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    account_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="client_record")
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self): return self.company or self.name

class Professional(TimeStamped):
    CATEGORIES = [(x,x.replace("_"," ").title()) for x in ["PRODUCTION_SOUND_RECORDIST","LOCATION_SOUND_RECORDIST","STUDIO_RECORDIST","FIELD_RECORDIST","BROADCAST_RECORDIST","LIVE_EVENT_RECORDIST","AUDIO_ENGINEER","BOOM_OPERATOR","SOUND_ASSISTANT","FOLEY_ARTIST","AUDIO_EDITOR"]]
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=40, choices=CATEGORIES, default="PRODUCTION_SOUND_RECORDIST")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    skills = models.TextField(blank=True)
    languages = models.CharField(max_length=200, blank=True)
    day_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    availability_notes = models.TextField(blank=True)
    portfolio_url = models.URLField(blank=True)
    verified = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self): return self.name

class Freelancer(TimeStamped):
    name = models.CharField(max_length=160)
    skill = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    available = models.BooleanField(default=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self): return self.name

class Service(TimeStamped):
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=40, default="day")
    base_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Project(TimeStamped):
    STATUS = [(x,x.replace("_"," ").title()) for x in ["ENQUIRY","QUOTATION","CONFIRMED","PRE_PRODUCTION","IN_PROGRESS","QC","CLIENT_REVIEW","COMPLETED","CANCELLED"]]
    CATEGORIES = [(x,x.replace("_"," ").title()) for x in ["FILM","TELEVISION","OTT","ADVERTISEMENT","DOCUMENTARY","CORPORATE","EVENT","MUSIC","PODCAST","NEWS","EDUCATION","GOVERNMENT","OTHER"]]
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=180)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="projects")
    category = models.CharField(max_length=30, choices=CATEGORIES, default="FILM")
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    recordists = models.ManyToManyField(Professional, blank=True, related_name="projects")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=240, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=STATUS, default="ENQUIRY")
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self): return f"{self.code} - {self.name}"

class Booking(TimeStamped):
    STATUS = [("REQUESTED","Requested"),("CONFIRMED","Confirmed"),("RESCHEDULED","Rescheduled"),("CANCELLED","Cancelled"),("COMPLETED","Completed")]
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    professional = models.ForeignKey(Professional, null=True, blank=True, on_delete=models.SET_NULL)
    service = models.ForeignKey(Service, null=True, blank=True, on_delete=models.SET_NULL)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    location = models.CharField(max_length=240, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="REQUESTED")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self): return f"Booking #{self.pk} - {self.client}"

class Equipment(TimeStamped):
    STATUS = [("AVAILABLE","Available"),("ALLOCATED","Allocated"),("MAINTENANCE","Maintenance"),("RETIRED","Retired"),("RENTED","Rented")]
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    asset_tag = models.CharField(max_length=50, unique=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    warranty_until = models.DateField(null=True, blank=True)
    condition = models.CharField(max_length=100, default="Good")
    status = models.CharField(max_length=20, choices=STATUS, default="AVAILABLE")
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    def __str__(self): return f"{self.asset_tag} - {self.name}"

class EquipmentAllocation(TimeStamped):
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    issued_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    issued_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    return_condition = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

class Studio(TimeStamped):
    name = models.CharField(max_length=160)
    room = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField(default=2)
    hourly_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    location = models.CharField(max_length=240, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class StudioSession(TimeStamped):
    studio = models.ForeignKey(Studio, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=30, default="BOOKED")

class RecordingSession(TimeStamped):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="sessions")
    recordist = models.ForeignKey(Professional, null=True, blank=True, on_delete=models.SET_NULL)
    session_date = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=240, blank=True)
    scene_number = models.CharField(max_length=50, blank=True)
    take_number = models.CharField(max_length=50, blank=True)
    timecode = models.CharField(max_length=80, blank=True)
    sample_rate = models.CharField(max_length=30, default="48000 Hz")
    bit_depth = models.CharField(max_length=20, default="24-bit")
    audio_format = models.CharField(max_length=20, default="WAV")
    duration_seconds = models.PositiveIntegerField(default=0)
    take_quality = models.CharField(max_length=20, default="GOOD")
    notes = models.TextField(blank=True)

class AudioAsset(TimeStamped):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="audio_assets")
    session = models.ForeignKey(RecordingSession, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=180)
    file = models.FileField(upload_to="audio/%Y/%m/")
    version = models.PositiveIntegerField(default=1)
    is_client_visible = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)
    def __str__(self): return self.title

class Quotation(TimeStamped):
    STATUS = [("DRAFT","Draft"),("SENT","Sent"),("ACCEPTED","Accepted"),("REJECTED","Rejected"),("EXPIRED","Expired")]
    number = models.CharField(max_length=40, unique=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    issue_date = models.DateField(default=timezone.localdate)
    valid_until = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS, default="DRAFT")
    terms = models.TextField(blank=True)
    def save(self,*args,**kwargs):
        self.gst_amount = (self.subtotal * self.gst_rate / Decimal("100")).quantize(Decimal("0.01"))
        self.total = self.subtotal + self.gst_amount
        super().save(*args,**kwargs)
    def __str__(self): return self.number

class Contract(TimeStamped):
    number = models.CharField(max_length=40, unique=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=180)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default="DRAFT")
    document = models.FileField(upload_to="contracts/", blank=True)
    terms = models.TextField(blank=True)

class Invoice(TimeStamped):
    STATUS = [("DRAFT","Draft"),("ISSUED","Issued"),("PART_PAID","Part Paid"),("PAID","Paid"),("OVERDUE","Overdue"),("CANCELLED","Cancelled")]
    number = models.CharField(max_length=40, unique=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    invoice_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(null=True, blank=True)
    place_of_supply = models.CharField(max_length=120, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS, default="DRAFT")
    notes = models.TextField(blank=True)
    def save(self,*args,**kwargs):
        self.gst_amount = (self.subtotal * self.gst_rate / Decimal("100")).quantize(Decimal("0.01"))
        self.total = self.subtotal + self.gst_amount
        if self.amount_paid >= self.total and self.total > 0: self.status = "PAID"
        elif self.amount_paid > 0 and self.status not in ["DRAFT","CANCELLED"]: self.status = "PART_PAID"
        super().save(*args,**kwargs)
    def __str__(self): return self.number

class Payment(TimeStamped):
    METHODS = [("CASH","Cash"),("BANK","Bank Transfer"),("UPI","UPI"),("CARD","Card"),("ONLINE","Online Gateway"),("CHEQUE","Cheque")]
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")
    receipt_number = models.CharField(max_length=40, unique=True)
    date = models.DateField(default=timezone.localdate)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHODS, default="BANK")
    reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        if self.invoice_id:
            self.invoice.amount_paid = sum(p.amount for p in self.invoice.payments.all())
            self.invoice.save()

class Expense(TimeStamped):
    date = models.DateField(default=timezone.localdate)
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=240)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    vendor = models.CharField(max_length=160, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL)

class Lead(TimeStamped):
    name = models.CharField(max_length=160)
    organisation = models.CharField(max_length=160, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    requirement = models.TextField(blank=True)
    source = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, default="NEW")
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

class Task(TimeStamped):
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default="OPEN")
    priority = models.CharField(max_length=20, default="MEDIUM")

class Document(TimeStamped):
    title = models.CharField(max_length=180)
    category = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to="documents/%Y/%m/")
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

class Review(TimeStamped):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    rating = models.PositiveSmallIntegerField(default=5)
    comments = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)

class Notification(TimeStamped):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=180)
    message = models.TextField()
    read = models.BooleanField(default=False)

class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=80, blank=True)
    detail = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]

class AgencySetting(TimeStamped):
    name = models.CharField(max_length=180, default="Sound Recordist Agency")
    tagline = models.CharField(max_length=240, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
