from django.db import models
from django.db import connection
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import F, Value
from django.conf import settings
from django.db import connection


class Login(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    otp = models.IntegerField(null=True, blank=True) 
    otp_created_at = models.DateTimeField(auto_now_add=True)  # Optional: to track OTP expiry

class Meta:
    managed=False
    db_table='beautyapp_login'

class ServiceTypes(models.Model):
    service_type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)

class Meta:
    managed=False
    db_table='beautyapp_servicetypes'


    def __str__(self):
        return self.type_name
    

class BeautyParlour(models.Model):
    name = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    star = models.IntegerField()  # Assuming star rating is an integer
    reviews = models.TextField()
    image = models.ImageField(upload_to='beauty_parlours/', null=True, blank=True)

class Meta:
    managed=False
    db_table='beautyapp_beautyparlour'

    def __str__(self):
        return self.name
    


class ServiceProvider(models.Model):
    provider_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)
    address = models.ForeignKey('Locations', on_delete=models.CASCADE)
    branch = models.ForeignKey('Branches', on_delete=models.CASCADE)
    service_type = models.ForeignKey('beautyapp.servicetypes', on_delete=models.CASCADE)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed=False
        db_table = 'branches'



    

class Beautician(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)  # e.g., 'Beautician', 'All Rounder'
    years_of_experience = models.CharField(max_length=100)
    rating = models.FloatField()  # Store rating as a float (e.g., 4.5)
    profile_image = models.ImageField(upload_to='beauticians/')  # Store profile images
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name

class Meta:
        managed=False
        db_table = 'beautyapp_beautician'
    

class FilterProvider(models.Model):
    name = models.CharField(max_length=255)
    rating = models.FloatField()
    address = models.ForeignKey('beautyapp.locations', on_delete=models.CASCADE)
    service_type = models.ForeignKey('beautyapp.servicetypes', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='provider_images/', blank=True, null=True)
    verified = models.BooleanField(default=False)


    
    @staticmethod
    def get_filtered_providers_with_details():
        query = """
            SELECT 
                fp.name,
                fp.rating,
                fp.address_id AS address_id,
                fp.service_type_id AS service_type_id,
                fp.image,
                fp.verified
            FROM 
                beautyapp_filterprovider AS fp
            JOIN 
                beautyapp_serviceprovider AS sp ON fp.address_id = sp.address_id
            
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        return results
class Meta:
        managed=False
        db_table = 'beautyapp_filterprovider'

    
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




class Photo(models.Model):
    
    photo_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='photos/')
    created_at = models.DateTimeField(auto_now_add=True)
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE,null=True)
    image_type=models.IntegerField(default=0)
   
class Meta:
        managed=False
        db_table = 'beautyapp_photo'
    

class FAQ(models.Model):
    faq_id= models.AutoField(primary_key=True)
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE,null=True)

class Meta:
        managed=False
        db_table = 'beautyapp_faq'


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

class Staff(models.Model):
    staff=models.AutoField(primary_key=True)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)  # e.g., Manager, Hairdresser, etc.
    years_of_experience = models.IntegerField(blank=True, null=True)
    available_slots = models.JSONField(null=True, blank=True)
    status = models.CharField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)


@staticmethod
def get_staff_with_provider_details_raw_sql():
    query = """
        SELECT 
            s.staff_id,
            s.name,
            s.role,
            s.status,
            s.created_at,
            sp.name,
            sp.rating,
            sp.image_url,
            sp.years_of_experience,
            sp.available_slots
        FROM 
            beautyapp_staff s
        JOIN 
            serviceproviders sp ON s.provider_id = sp.provider_id
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return results



class Meta:
        managed=False
        db_table = 'beautyapp_staff'


class Category(models.Model):

    category_id= models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)  
    status = models.CharField(max_length=20, default='Active')

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



class Serviceprovidertype(models.Model):
    provider_service_id = models.AutoField(primary_key=True)
    provider_id= models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    service_id = models.ForeignKey(Services, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # Duration in minutes
    status = models.CharField(max_length=20, default='Active')

    def get_provider_services_with_cursor(self, service_id, lat, lng, radius, service_type_id=None, category_id=None):
     # Haversine formula using latitude and longitude
     
    #  print('category_id',category_id)
     
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
     SELECT DISTINCT
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
     """
     
     # Add WHERE clause with mandatory filters
     if service_id is not None and int(service_id) != 0:
        # print(service_id)
        # print(5454545)
        query += "WHERE s.service_id = %s "     
     else:
        query += "WHERE s.category_id = %s "
     
     # Add optional filter for service_type_id if provided
     if service_type_id:
         query += " AND st.service_type_id = %s "
     
     # Add optional filter for category_id if provided
     #if category_id:
         #query += " AND s.category_id = %s "
 
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
     
    
     params = [lat, lng, lat]

     #print(service_id,'service_id')

     if  service_id is not None and int(service_id) != 0:
        #print('123456')
       
        params.append(service_id)

     else:
        params.append(category_id)


     # Add service_type_id to the parameters if provided
     if service_type_id:
         params.append(service_type_id)
     
     # Add category_id to the parameters if provided
    #  if category_id:
    #      params.append(category_id)
 
     # Add parameters for the Haversine formula and radius filter
     params.extend([lat, lng, lat, radius])

    #  print("Query:", query)
    #  print("Params:", params)
 
     # Execute the query
     with connection.cursor() as cursor:
         cursor.execute(query, params)
         results = cursor.fetchall()
 
         # Get column names from the cursor description
         columns = [col[0] for col in cursor.description]
    #formatted_query = query % tuple([repr(param) for param in params])
 
     data = []
     for row in results:
         row_dict = dict(zip(columns, row))
         # Build the correct image URL using BASE_URL and MEDIA_URL from settings
         image_url = row_dict.get('image_url')
         if image_url:
             row_dict['image_url'] = f"{settings.BASE_URL}{settings.MEDIA_URL}{image_url}"
 
         data.append(row_dict)

        # Deduplication function
     def get_distinct_results(query_result):
            unique_provider_ids = set()
            distinct_data = []

            for row_dict in query_result:
                provider_id = row_dict.get("provider_id")
                if provider_id not in unique_provider_ids:
                    unique_provider_ids.add(provider_id)
                    distinct_data.append(row_dict)
            
            return distinct_data

        # Call the deduplication function with 'data'
     distinct_data = get_distinct_results(data)

        # Return the distinct result
     return distinct_data
         
    #return data

    
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



class StaffReview(models.Model):
     review_id=models.AutoField(primary_key=True)
     staff=models.ForeignKey(Staff, on_delete=models.CASCADE)
     user=models.ForeignKey(User, on_delete=models.CASCADE)       
     rating = models.FloatField()
     review = models.TextField(max_length=255)
     created_at = models.DateTimeField(default=timezone.now)


def get_staff_reviews():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT sr.review_id, s.name as staff_name, s.role as staff_role, 
                   u.name as user_name, u.email as user_email, 
                   sr.rating, sr.review, sr.created_at
            FROM StaffReview sr
            JOIN Staff s ON sr.staff_id = s.staff
            JOIN User u ON sr.user_id = u.user_id
        """)
        results = cursor.fetchall()

    return results



class Meta:
        managed=False
        db_table = 'beautyapp_staffreview'



class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE)
    branch = models.ForeignKey('Branches', on_delete=models.SET_NULL, null=True, blank=True)  
    appointment_date = models.DateField(default=timezone.now().date)  
    appointment_time = models.TimeField(default=timezone.now().time)  
    status = models.ForeignKey('Status', on_delete=models.CASCADE, default=0)
    otp = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    service_id_new =models.TextField()
    quantity = models.TextField() 

    
class Meta:
        managed = False
        db_table = 'beautyapp_appointment'


class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = False  
        db_table = 'beautyapp_status'

    def __str__(self):
        return self.status_name         


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
        

class CustomerFeedback(models.Model):
    userfeedback_id=models.AutoField(primary_key=True)
    user_name = models.ForeignKey('User', on_delete=models.CASCADE, related_name='feedback_by_user')
    email =models.ForeignKey('User', on_delete=models.CASCADE, related_name='feedback_email') 
    feedback = models.TextField()
    profile_image = models.ImageField(upload_to='profile_images/')


    def get_feedback_with_user_info():
      with connection.cursor() as cursor:
        # Define the SQL query
        sql_query = """
            SELECT cf.userfeedback_id, u1.name AS user_name, u2.email AS user_email, cf.feedback
            FROM CustomerFeedback cf
            INNER JOIN User u1 ON cf.user_name_id = u1.user_id
            INNER JOIN User u2 ON cf.email_id = u2.user_id;
        """
        # Execute the query
        cursor.execute(sql_query)
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Process the results (convert to a list of dictionaries for easier use)
        feedback_list = []
        for row in results:
            feedback_list.append({
                'userfeedback_id': row[0],
                'user_name': row[1],
                'user_email': row[2],
                'feedback': row[3],
            })
        
        return feedback_list

class Meta:
        managed=False
        db_table = 'beautyapp_customerfeedback'


class Review(models.Model):
    review_id=models.AutoField(primary_key=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    comment = models.TextField()
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='reviews')
    user_id = models.IntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



class Meta:
        managed=False
        db_table = 'beautyapp_review'

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    provider = models.ForeignKey('ServiceProvider', on_delete=models.CASCADE)  # Assuming the provider exists
    coupon_code = models.CharField(max_length=100, unique=True)
    coupon_limit = models.IntegerField()
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    discount_type = models.CharField(max_length=50, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField()  
    created_datetime = models.DateTimeField(auto_now_add=True)

class Meta:
        managed=False
        db_table = 'beautyapp_coupon'

class ServiceFAQ(models.Model):
    faq_id = models.AutoField(primary_key=True)
    service_type = models.IntegerField()
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class Meta:
        managed=False
        db_table = 'beautyapp_servicefaq'

class BeautyAppPackage(models.Model):
    id = models.AutoField(primary_key=True)
    provider_id = models.IntegerField()
    package_name = models.CharField(max_length=255)
    package_image = models.ImageField(upload_to='package_images/')  # Use ImageField for handling file uploads
    package_amount = models.DecimalField(max_digits=10, decimal_places=2)
    package_services = models.TextField()  # Use TextField for longer content
    status = models.IntegerField()

class Meta:
        managed=False
        db_table = 'beautyapp_packages'
