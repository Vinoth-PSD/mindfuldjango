from django.db import models
from django.db import connection
from django.utils import timezone
import os
from django.conf import settings
from django.db.models import Sum
from .storages import AzureMediaStorage


# class Login(models.Model):
#     phone = models.CharField(max_length=15, unique=True)
#     otp = models.IntegerField(null=True, blank=True) 
#     otp_created_at = models.DateTimeField(auto_now_add=True)  # Optional: to track OTP expiry

# class Meta:
#     managed= False
#     db_table='beautyapp_login'

class ServiceProvider(models.Model):
    provider_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)
    address = models.ForeignKey('Locations', on_delete=models.CASCADE)
    branch = models.ForeignKey('Branches', on_delete=models.CASCADE)
    service_type = models.ForeignKey('beautyapp.ServiceTypes', on_delete=models.CASCADE,related_name='service_service_providers')
    years_of_experience = models.IntegerField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    specializations = models.TextField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    working_hours = models.TextField(null=True, blank=True)
    available_slots = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #image_url = models.ImageField(upload_to='provider_images/', null=True, blank=True)
    image_url = models.ImageField(upload_to='provider_images/', storage=AzureMediaStorage(), null=True, blank=True)  
    business_summary = models.TextField(blank=True, null=True)
    gender_type = models.CharField(max_length=100, blank=True, null=True)  
    timings = models.CharField(max_length=100, blank=True, null=True)
    owner_name = models.CharField(max_length=100, blank=True, null=True)  
    established_on = models.DateField(null=True, blank=True)  
    services_offered = models.TextField(blank=True, null=True)  
    staff_information = models.TextField(blank=True, null=True)  
    salon_facilities = models.TextField(blank=True, null=True)  
    cancellation_policy = models.TextField(blank=True, null=True)  
    #home_address = models.TextField(null=True, blank=True)  
    years_of_experience = models.IntegerField(null=True, blank=True)  
    languages_spoken = models.TextField(null=True, blank=True)  
    travel_capability_kms = models.IntegerField(null=True, blank=True)  
    certifications = models.FileField(upload_to='certifications/', null=True, blank=True) 
    willing_to_work_holidays = models.TextField(null=True, blank=True)
    otp = models.IntegerField(null=True, blank=True) 
    otp_created_at = models.DateField(auto_now_add=True)  
    available_credits = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_deleted = models.BooleanField(default=False)  # Soft delete field



    class Meta:
         managed=False
         db_table = 'serviceproviders'

    def __str__(self):
        return self.name
    



class Locations(models.Model):
    location_id = models.AutoField(primary_key=True)
    address_line1 = models.CharField(max_length=255 , blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=100 , blank=True, null=True)
    postal_code = models.IntegerField(max_length=20 ,blank=True, null=True)
    country = models.CharField(max_length=100 ,blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6 ,blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed=False
        db_table = 'locations'  # This sets the table name explicitly

    
class Branches(models.Model):
    branch_id = models.AutoField(primary_key=True)
    branch_name = models.CharField(max_length=255)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE, related_name='branches')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='branches')  
    phone = models.CharField(max_length=20, null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #logo = models.ImageField(upload_to='branch_logos/', null=True, blank=True) 
    logo = models.ImageField(upload_to='branch_logos/', storage=AzureMediaStorage(),null=True, blank=True) 
    
    service_status = models.IntegerField(choices=[(1, 'Online'), (0, 'Offline')], default=0)
    is_deleted = models.BooleanField(default=False)  # New column



    class Meta:
        managed=False
        db_table = 'branches'

class ServiceTypes(models.Model):
    service_type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

class Meta:
    managed=False
    db_table='beautyapp_servicetypes'


    def __str__(self):
        return self.type_name 
    
class ProviderBankDetails(models.Model):
    id = models.AutoField(primary_key=True)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    account_holder_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=50)
    account_type = models.CharField(max_length=50, null=True, blank=True)
    bank_branch = models.CharField(max_length=255, null=True, blank=True)
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        managed=False
        db_table = 'provider_bank_details'


def get_provider_upload_to(instance, filename):
    # Define the path where all files will be stored in the provider's specific folder
    provider_id = instance.provider.pk  
    return os.path.join(f'serviceprovider/{provider_id}/{filename}')

class ProviderTaxRegistration(models.Model):
    id = models.AutoField(primary_key=True)
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE)
    tax_identification_number = models.CharField(max_length=50)
    tax_file = models.FileField(upload_to=get_provider_upload_to, null=True, blank=True)
    gst_number = models.CharField(max_length=50)
    gst_file = models.FileField(upload_to=get_provider_upload_to, null=True, blank=True)
    proof_of_identity_type = models.CharField(max_length=50)
    proof_of_identity_number = models.CharField(max_length=50)
    identity_file = models.FileField(upload_to=get_provider_upload_to, null=True, blank=True)
    proof_of_address_type = models.CharField(max_length=50)
    address_file = models.FileField(upload_to=get_provider_upload_to, null=True, blank=True)

    class Meta:
        managed=False
        db_table = 'provider_tax_details'

    def __str__(self):
        return f"Tax registration for {self.provider.name}"
    

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)


    class Meta:
        managed=False
        db_table = 'provider_roles'

    def __str__(self):
        return self.role_name
    
class Staff(models.Model):
    staff = models.AutoField(primary_key=True)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branches, on_delete=models.SET_NULL, null=True, blank=True)  # Direct relationship with Branches
    name = models.CharField(max_length=100)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)  
    years_of_experience = models.IntegerField(blank=True, null=True)
    available_slots = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, blank=True, null=True)  # Added max_length
    created_at = models.DateTimeField(auto_now_add=True)
    #photo = models.ImageField(upload_to='staff_photos/', null=True, blank=True)  # Added ImageField for photo upload
    photo = models.ImageField(upload_to='staff_photos/', storage=AzureMediaStorage(),null=True, blank=True)
    
    is_deleted = models.BooleanField(default=False)  # New field for soft deletion
    phone = models.CharField(max_length=15, blank=True, null=True)  # Added phone field
    otp = models.IntegerField(blank=True, null=True)  # Added otp field



    class Meta:
        managed = False  
        db_table = 'beautyapp_staff'  

class Review(models.Model):
    review_id=models.AutoField(primary_key=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    comment = models.TextField()
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='reviews')
    user_id = models.IntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=255, blank=True, null=True)  # Add order_id field
    status = models.IntegerField(
        choices=[(0, 'Inactive'), (1, 'Active')],
        null=True,  
        blank=True,  
    )




    class Meta:
        managed=False
        db_table = 'beautyapp_review'

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)  
    created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)



    class Meta:
        managed=False
        db_table = 'beautyapp_user'


class Category(models.Model):

    category_id= models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='Active')
    #image = models.ImageField(upload_to='categories/', null=True, blank=True)
    image = models.ImageField(upload_to='categories/', storage=AzureMediaStorage(), null=True, blank=True) 
    is_deleted = models.BooleanField(default=False)  



    class Meta:
        managed=False
        db_table = 'beautyapp_category'

class Subcategory(models.Model):
    
    subcategory_id= models.AutoField(primary_key=True)
    subcategory_name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='Active')
    is_deleted = models.BooleanField(default=False)  


    class Meta:
        managed=False
        db_table = 'beautyapp_subcategory'


class Services(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey('Subcategory', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, default='Active')
    #image = models.ImageField(upload_to='service_images/', null=True, blank=True)
    image = models.ImageField(upload_to='service_images/',storage=AzureMediaStorage(), null=True, blank=True)
    sku_value = models.CharField(max_length=255, null=True)
    service_time = models.CharField(max_length=50, null=True, blank=True)
    service_type = models.IntegerField(null=True, blank=True)
    package_services = models.TextField(null=True, blank=True)
    provider= models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE, null=True, blank=True)  
    package_services_ids = models.TextField(null=True, blank=True)  # New field for storing service IDs
    is_deleted = models.BooleanField(default=False)  




    class Meta:
        managed = False
        db_table = 'beautyapp_services'

    def __str__(self):
        return self.service_name



class Serviceprovidertype(models.Model):
    provider_service_id = models.AutoField(primary_key=True)
    provider_id= models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    service_id = models.ForeignKey(Services, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE)  # Use `branch` instead of `branch_id`
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    duration = models.CharField(max_length=50, null=True, blank=True)  # Store duration as a string
    status = models.CharField(max_length=20, default='Active')
    is_deleted = models.BooleanField(default=False)  # New field to handle soft deletion


    class Meta:
        managed=False
        db_table = 'beautyapp_serviceprovidertype'

    def __str__(self):
        return f"{self.provider.name} - {self.service.service_name}"

class Permissions(models.Model):
    permission_id = models.AutoField(primary_key=True)  
    role = models.ForeignKey('Role', on_delete=models.CASCADE) 
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE, null=True, blank=True)  
    dashboard = models.BooleanField(default=False)  
    manage_role = models.BooleanField(default=False) 
    service_listing = models.BooleanField(default=False)  
    service_management = models.BooleanField(default=False)  
    sales_transactions = models.BooleanField(default=False)  
    ratings_reviews = models.BooleanField(default=False)  
    report_details = models.BooleanField(default=False)  
    roles_management = models.BooleanField(default=False)
    staff_management = models.BooleanField(default=False)
    branch_management = models.BooleanField(default=False)
    all_booking = models.BooleanField(default=False)
    schedule = models.BooleanField(default=False)
    inprogress = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)

    class Meta:
        db_table = 'permissions'

    def __str__(self):
        return f"Permissions for Role ID: {self.role_id}"
    
class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE)
    branch = models.ForeignKey('Branches', on_delete=models.SET_NULL, null=True, blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.ForeignKey('Status', on_delete=models.CASCADE, default=0)
    otp = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    service_id_new = models.TextField()
    quantity = models.TextField()
    message = models.CharField(max_length=255, null=True, blank=True)  
    stylist = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True, default=None) 
    used_credits = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New Field
 


    class Meta:
        db_table = 'beautyapp_appointment'  
        managed = False  

    def __str__(self):
        return f"Appointment {self.appointment_id} - {self.appointment_date}"
         

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(max_length=20, default='Not Paid')
    coupon_code = models.CharField(max_length=50, null=True, blank=True)
    coupon_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_mode = models.CharField(
        max_length=20,
        choices=[
            ('Cash', 'Cash'),
            ('Card', 'Card'),
            ('Online', 'Online'),
            ('UPI', 'UPI'),
        ],
        default='Cash',
    )
    sgst = models.IntegerField()  # SGST field as integer
    cgst = models.IntegerField()  # CGST field as integer
    grand_total = models.IntegerField()  # Grand total field as integer



    class Meta:
        managed = False
        db_table = 'beautyapp_payment'

    def __str__(self):
        return (
            f"Payment ID: {self.payment_id}, Amount: {self.amount}, "
            f"Status: {self.payment_status}, Mode: {self.payment_mode}, "
            f"SGST: {self.sgst}, CGST: {self.cgst}, Grand Total: {self.grand_total}, "
            f"Date: {self.payment_date}"
        )


class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = False  
        db_table = 'beautyapp_status'

    def __str__(self):
        return self.status_name

class Beautician(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)  # e.g., 'Beautician', 'All Rounder'
    years_of_experience = models.CharField(max_length=100)
    rating = models.FloatField()  # Store rating as a float (e.g., 4.5)
    # profile_image = models.ImageField(upload_to='beauticians/')  # Store profile images
    profile_image = models.ImageField(upload_to='beauticians/', storage=AzureMediaStorage()) 
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE,null=True)


    class Meta:
        managed=False
        db_table = 'beautyapp_beautician'

    def __str__(self):
        return self.name


class Message(models.Model):
    message_id = models.AutoField(primary_key=True)  
    text = models.CharField(max_length=255)        
    type = models.CharField(max_length=50)   

    class Meta:
        managed=False
        db_table = 'messages'       

    def __str__(self):
        return self.text
    
class ProviderTransactions(models.Model):
    id = models.AutoField(primary_key=True)
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=50)
    payment_type = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Razorpay Payment ID
    order_id = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Razorpay Order ID
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Success", "Success"), ("Failed", "Failed")],
        default="Pending"
    )  # Default to Pending
    pay_id = models.CharField(max_length=10, unique=True, blank=True, null=True)  # MB001 Format
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Changed to DecimalField
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Changed to DecimalField

    class Meta:
        db_table = 'provider_transactions'

    def save(self, *args, **kwargs):
        if not self.pay_id:  # Generate pay_id only if it's not set
            last_transaction = ProviderTransactions.objects.order_by('-id').first()
            if last_transaction and last_transaction.pay_id:
                last_number = int(last_transaction.pay_id[2:])  # Extract number from "MB001"
                new_number = last_number + 1
            else:
                new_number = 1
            self.pay_id = f"MB{new_number:03d}"  # Format as MB001, MB002, etc.

        super(ProviderTransactions, self).save(*args, **kwargs)

    def __str__(self):
        return f'Transaction {self.pay_id} - {self.status}'

    
class AdminUser(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=255, default="superadmin")
    otp = models.CharField(max_length=10, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'adminuser'

    def __str__(self):
        return self.username
    
class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('flat', 'Flat'),  # Matches your database value

    ]

    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE)  
    coupon_code = models.CharField(max_length=100, unique=True)
    coupon_limit = models.IntegerField()
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    discount_type = models.CharField(max_length=50, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField()  
    created_datetime = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


    class Meta:
        managed = False  # Prevents Django from creating/migrating this table
        db_table = 'beautyapp_coupon'  # Explicitly set the correct table name

    def __str__(self):
        return self.coupon_code

    