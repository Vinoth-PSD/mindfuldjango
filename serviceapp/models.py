from django.db import models
from django.db import connection
from django.utils import timezone
import os
from django.conf import settings


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
    status = models.CharField(max_length=20, default='Active')
    working_hours = models.TextField(null=True, blank=True)
    available_slots = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_url = models.ImageField(upload_to='provider_images/', null=True, blank=True)
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

    @staticmethod
    def get_service_providers_with_details():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    sp.provider_id,
                    sp.name AS provider_name,
                    sp.email,
                    sp.phone,
                    sp.years_of_experience,
                    sp.skills,
                    sp.specializations,
                    sp.rating,
                    sp.status,
                    sp.working_hours,
                    sp.available_slots,
                    sp.created_at,
                    sp.updated_at,
                    sp.image_url,
                    l.address_line1,
                    l.address_line2,
                    l.city,
                    l.state,
                    l.postal_code,
                    l.country,
                    l.latitude,
                    l.longitude,
                    st.type_name AS service_type_name
                FROM 
                    ServiceProviders sp
                JOIN 
                    Locations l ON sp.address_id = l.location_id
                JOIN 
                    ServiceTypes st ON sp.service_type_id = st.service_type_id
            """)
            results = cursor.fetchall()
        return results


    class Meta:
         managed=False
         db_table = 'serviceproviders'

    def __str__(self):
        return self.name
    



class Locations(models.Model):
    location_id = models.AutoField(primary_key=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed=False
        db_table = 'locations'  # This sets the table name explicitly

    
class Branches(models.Model):
    branch_id = models.AutoField(primary_key=True)
    branch_name = models.CharField(max_length=100)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE, related_name='branches')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='branches')  
    phone = models.CharField(max_length=20, null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    logo = models.ImageField(upload_to='branch_logos/', null=True, blank=True) 
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
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='staff_photos/', null=True, blank=True)  # Added ImageField for photo upload
    is_deleted = models.BooleanField(default=False)  # New field for soft deletion



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




    class Meta:
        managed=False
        db_table = 'beautyapp_review'

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)



    class Meta:
        managed=False
        db_table = 'beautyapp_user'


class Category(models.Model):

    category_id= models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='Active')
    image = models.ImageField(upload_to='categories/', null=True, blank=True)  


    class Meta:
        managed=False
        db_table = 'beautyapp_category'

class Subcategory(models.Model):
    
    subcategory_id= models.AutoField(primary_key=True)
    subcategory_name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='Active')

    class Meta:
        managed=False
        db_table = 'beautyapp_subcategory'


class Services(models.Model):
    service_id=models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey('Subcategory', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, default='Active')
    image = models.ImageField(upload_to='service_images/',null=True, blank=True)
    sku_value= models.CharField(max_length=255,null=True)
    service_time = models.CharField(max_length=50, null=True, blank=True)


    class Meta:
        managed=False
        db_table = 'beautyapp_services'


class Serviceprovidertype(models.Model):
    provider_service_id = models.AutoField(primary_key=True)
    provider_id= models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    service_id = models.ForeignKey(Services, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE)  # Use `branch` instead of `branch_id`
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # Duration in minutes
    status = models.CharField(max_length=20, default='Active')
    is_deleted = models.BooleanField(default=False)  # New field to handle soft deletion

    def get_provider_services_with_cursor(self, service_id, lat, lng, radius, service_type_id=None):
        # Haversine formula using latitude and longitude
        haversine_formula = """
        ROUND(
        CAST(
            6371 * acos(
                cos(radians(%s)) * cos(radians(loc.latitude)) 
                * cos(radians(loc.longitude) - radians(%s)) 
                + sin(radians(%s)) * sin(radians(loc.latitude))
            ) AS numeric
        ), 1
        )
        """

        query = f"""
        SELECT 
        sp.provider_id,
        sp.name AS provider_name,
        sp.rating,
        sp.image_url,
        sp.business_summary,
        sp.gender_type,
        sp.timings,
        loc.latitude AS provider_latitude,
        loc.longitude AS provider_longitude,
        loc.city AS provider_city,
        loc.state AS provider_state,
        s.service_name,
        s.service_id,
        ps.price,
        br.branch_id,
        br.branch_name,
        branch_loc.latitude AS branch_latitude,
        branch_loc.longitude AS branch_longitude,
        branch_loc.city AS branch_city,
        branch_loc.state AS branch_state,
        st.service_type_id,  -- Select service_type_id
        {haversine_formula} AS distance_km,  -- Calculate distance in kilometers between provider and branch
        TRUE AS verified , 
        '69.2K reviews' AS review_count,  -- Static value for review count   
        '1234' AS otp, -- Set default OTP  
         s.service_name AS all_services
        FROM 
            ServiceProviders sp
        JOIN 
            beautyapp_serviceprovidertype ps ON sp.provider_id = ps.provider_id_id
        JOIN 
            beautyapp_Services s ON ps.service_id_id = s.service_id
        JOIN 
            Locations loc ON sp.address_id = loc.location_id  -- Provider's main location
        LEFT JOIN 
            Branches br ON sp.branch_id = br.branch_id
        LEFT JOIN 
            Locations branch_loc ON br.location_id = branch_loc.location_id  -- Branch location
        LEFT JOIN 
            beautyapp_servicetypes st ON sp.service_type_id = st.service_type_id  -- Join ServiceTypes
        WHERE 
            s.service_id = %s
        """
        # Add the optional filter for service_type_id if provided
        if service_type_id:
            query += " AND st.service_type_id = %s "

        query += f""" 
        GROUP BY 
            sp.provider_id, sp.name, sp.rating, loc.latitude, loc.longitude, loc.city, loc.state, 
            s.service_name, s.service_id, ps.price, br.branch_id, br.branch_name, 
            branch_loc.latitude, branch_loc.longitude, branch_loc.city, branch_loc.state,
            st.service_type_id
        HAVING 
            {haversine_formula} <= %s  -- Apply radius filter in kilometers
        ORDER BY 
            distance_km ASC  -- Order results by distance in ascending order

        """

        # Parameters to be passed to the query
        params = [lat, lng, lat, service_id]

        # Add service_type_id to the parameters if provided
        if service_type_id:
            params.append(service_type_id)
        
        params.extend([lat, lng, lat, radius])

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

            # Get column names from the cursor description
            columns = [col[0] for col in cursor.description]

        data = []
        for row in results:
            row_dict = dict(zip(columns, row))
            # Build the correct image URL using BASE_URL and MEDIA_URL from settings
            image_url = row_dict.get('image_url')
            if image_url:
                row_dict['image_url'] = f"{settings.BASE_URL}{settings.MEDIA_URL}{image_url}"

            data.append(row_dict)
            
        return data
    
    # Method to get provider details
    def get_provider_details(self, provider_id):
        query = """
        SELECT 
            sp.provider_id,
            sp.name AS provider_name,
            sp.rating,
            sp.image_url,
            loc.latitude AS provider_latitude,
            loc.longitude AS provider_longitude,
            loc.city AS provider_city,
            loc.state AS provider_state,
            br.branch_id,
            br.branch_name,
            branch_loc.latitude AS branch_latitude,
            branch_loc.longitude AS branch_longitude,
            branch_loc.city AS branch_city,
            branch_loc.state AS branch_state,
            TRUE AS verified
        FROM 
            ServiceProviders sp
        JOIN 
            Locations loc ON sp.address_id = loc.location_id
        LEFT JOIN 
            Branches br ON sp.branch_id = br.branch_id
        LEFT JOIN 
            Locations branch_loc ON br.location_id = branch_loc.location_id
        WHERE 
            sp.provider_id = %s
        """
        params = [provider_id]
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

            columns = [col[0] for col in cursor.description]

            # Prepare the result by zipping columns with row data
        data = []
        for row in results:
            row_dict = dict(zip(columns, row))

            # Append the base URL and media URL to image_url if it exists
            image_url = row_dict.get('image_url')
            if image_url:
                row_dict['image_url'] = f"{settings.BASE_URL}{settings.MEDIA_URL}{image_url}"

            data.append(row_dict)

        return data

    # Method to get services for the provider
    def get_provider_services(self, provider_id, prioritize_service_id=None):
        query = """
        SELECT 
            s.service_name,
            s.service_id,
            s.price,
            s.image,
            s.description,
            s.service_time
        FROM 
            ServiceProviders sp
        JOIN 
            beautyapp_serviceprovidertype ps ON sp.provider_id = ps.provider_id_id
        JOIN 
            beautyapp_Services s ON ps.service_id_id = s.service_id
        JOIN 
            Locations loc ON sp.address_id = loc.location_id
        LEFT JOIN 
            Branches br ON sp.branch_id = br.branch_id
        LEFT JOIN 
            Locations branch_loc ON br.location_id = branch_loc.location_id
        WHERE 
            sp.provider_id = %s
        """
        
        # Add ORDER BY to prioritize the given service_id if provided
        if prioritize_service_id:
            query += """
            ORDER BY 
                CASE 
                    WHEN s.service_id = %s THEN 0  -- prioritize this service_id
                    ELSE 1
                END, 
                s.service_name ASC  -- additional ordering by service_name
            """
            params = [provider_id, prioritize_service_id]
        else:
            query += " ORDER BY s.service_name ASC"  # Default ordering by service_name
            params = [provider_id]
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

            columns = [col[0] for col in cursor.description]
            # Prepare the result by zipping columns with row data
            data = [dict(zip(columns, row)) for row in results]

        # Build the correct image URL using BASE_URL and MEDIA_URL from settings
        for row in data:
            image = row.get('image')
            if image:
                row['image'] = f"{settings.BASE_URL}{settings.MEDIA_URL}{image}"

        return data
    
        
    def get_beauticians_for_provider(self, provider_id):
        query = """
        SELECT 
            b.id AS beautician_id,
            b.name AS beautician_name,
            b.role,
            b.years_of_experience,
            b.rating,
            b.profile_image
        FROM 
            beautyapp_beautician b
        WHERE 
            b.provider_id = %s
        """
        params = [provider_id]
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

            columns = [col[0] for col in cursor.description]
            # Prepare the result by zipping columns with row data
            data = [dict(zip(columns, row)) for row in results]

        # Build the correct image URL using BASE_URL and MEDIA_URL from settings
        for row in data:
            profile_image = row.get('profile_image')
            if profile_image:
                row['profile_image'] = f"{settings.BASE_URL}{settings.MEDIA_URL}{profile_image}"

        return data
    
    def get_provider_photos(self, provider_id,image_type):
        query = """
        SELECT 
            p.photo_id,
            p.image,
            p.created_at
        FROM 
            beautyapp_photo p

        WHERE 
            p.provider_id = %s AND p.image_type = %s
        """
        params = [provider_id,image_type]
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in results]

        # Build the correct image URL using BASE_URL and MEDIA_URL from settings
        for row in data:
            image_url = row.get('image')
            if image_url:
                row['image'] = f"{settings.BASE_URL}{settings.MEDIA_URL}{image_url}"

        return data
    
    def get_faqs_for_provider(self, provider_id):
        query = """
        SELECT 
            f.faq_id,
            f.question,
            f.answer,
            f.created_at,
            f.updated_at
        FROM 
            beautyapp_faq f
        WHERE 
            f.provider_id = %s
        """
        params = [provider_id]
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

            columns = [col[0] for col in cursor.description]
            # Prepare the result by zipping columns with row data
            data = [dict(zip(columns, row)) for row in results]

        return data
    
    def get_overview_for_provider(self, provider_id):
        try:
            provider = ServiceProvider.objects.select_related('address').get(provider_id=provider_id)

            overview_data = {
                'business_summary': provider.business_summary,
                'gender_type': provider.gender_type,
                'timings': provider.timings,
                'latitude': provider.address.latitude,
                'longitude': provider.address.longitude
            }
            return overview_data
        except ServiceProvider.DoesNotExist:
            return None
    
    def get_reviews_by_provider(self,provider_id):
        query = """
            SELECT 
        CASE 
            WHEN r.user_id IS NULL OR u.user_id IS NULL THEN 'Anonymous' 
            ELSE u.name 
        END as user_name,
        r.review_id, 
        r.rating, 
        r.comment,
        r.created_at
    FROM 
        beautyapp_review r
    LEFT JOIN 
        beautyapp_user u ON r.user_id = u.user_id
    WHERE 
        r.provider_id = %s;

        """
        params = [provider_id]
        
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Fetch column names from the cursor description for zipping
            columns = [col[0] for col in cursor.description]
            # Prepare the result by zipping column names with row data
            reviews = [dict(zip(columns, row)) for row in results]

        return reviews
    
    def get_provider_packages(self, provider_id):
        query = """
        SELECT 
            bp.id AS package_id,
            bp.package_name,
            bp.package_image,
            bp.package_amount,
            bp.package_services,
            bp.status
        FROM 
            beautyapp_packages bp
        WHERE 
            bp.provider_id = %s
        """
        params = [provider_id]
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

            columns = [col[0] for col in cursor.description]

        data = []
        for row in results:
            row_dict = dict(zip(columns, row))

            # Append the base URL and media URL to package_image if it exists
            package_image = row_dict.get('package_image')
            if package_image:
                row_dict['package_image'] = f"{settings.BASE_URL}{settings.MEDIA_URL}{package_image}"

            # Convert package_services string to a list
            package_services = row_dict.get('package_services')
            if package_services:
                row_dict['package_services'] = package_services.strip('{}').split(',')

            data.append(row_dict)

        return data


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

    class Meta:
        db_table = 'beautyapp_appointment'  
        managed = False  # Ensure no migrations are made for this table

    def __str__(self):
        return f"Appointment {self.appointment_id} - {self.appointment_date}"
         

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(max_length=20, default='Pending')
    coupon_code = models.CharField(max_length=50, null=True, blank=True)
    coupon_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        managed = False 
        db_table = 'beautyapp_payment'

class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = False  
        db_table = 'beautyapp_status'

    def __str__(self):
        return self.status_name


