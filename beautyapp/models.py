from django.db import models
from django.db import connection
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import F, Value
from django.conf import settings
from django.db import connection
from django.utils.timezone import now
from .storages import AzureMediaStorage
import re
from datetime import datetime


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
    salon_facilities = models.TextField(null=True, blank=True)
    languages_spoken = models.TextField(null=True, blank=True)
    travel_capability_kms = models.IntegerField(null=True, blank=True)
    available_slots = models.JSONField(null=True, blank=True)
    established_on= models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_url = models.ImageField(upload_to='provider_images/', null=True, blank=True)
    business_summary = models.TextField(blank=True, null=True)
    gender_type = models.CharField(max_length=100, blank=True, null=True)  
    timings = models.CharField(max_length=100, blank=True, null=True)
    available_credits = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_deleted = models.BooleanField(default=False)  # Soft delete field


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
    provider=models.ForeignKey('ServiceProvider', on_delete=models.CASCADE)
    service_status = models.IntegerField(choices=[(1, 'Online'), (0, 'Offline')], default=0)
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
    is_deleted = models.BooleanField(default=False)  
 


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
    dob = models.DateField(null=True, blank=True)  # Date of birth field
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        null=True,
        blank=True
    )  # Gender field with choices
    location = models.CharField(max_length=255, null=True, blank=True)  # Location field
    address = models.CharField(max_length=255, null=True, blank=True)  # Address field
    created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'beautyapp_user'

    def __str__(self):
        return self.name

class Staff(models.Model):
    staff=models.AutoField(primary_key=True)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)  
    years_of_experience = models.IntegerField(blank=True, null=True)
    available_slots = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, blank=True, null=True)  # Added max_length
    created_at = models.DateTimeField(default=timezone.now)
    phone = models.CharField(max_length=15, blank=True, null=True) 
    otp = models.IntegerField(blank=True, null=True)  
    photo = models.ImageField(upload_to='staff_photos/', storage=AzureMediaStorage(),null=True, blank=True)



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


class Serviceprovidertype(models.Model):
    provider_service_id = models.AutoField(primary_key=True)
    provider_id= models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    service_id = models.ForeignKey(Services, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # Duration in minutes
    status = models.CharField(max_length=20, default='Active')
    is_deleted = models.BooleanField(default=False)  
    package_services = models.TextField(null=True, blank=True)
    package_services_ids = models.TextField(null=True, blank=True) 
    service_type = models.IntegerField(null=True, blank=True)  
    package_name = models.CharField(max_length=255, null=True, blank=True)  

    def get_provider_services_with_cursor(self, service_id, lat, lng, radius, service_type_id=None, category_id=None):
     # Haversine formula using latitude and longitude
     
    #  print('category_id',category_id)
     
     haversine_formula = """
     ROUND(
     CAST(
         6371 * acos(
             cos(radians(%s)) * cos(radians(branch_loc.latitude)) 
             * cos(radians(branch_loc.longitude) - radians(%s)) 
             + sin(radians(%s)) * sin(radians(branch_loc.latitude))
         ) AS numeric
     ), 1
     )
     """
 
     query = f"""
SELECT 
     br.branch_id,
     br.branch_name,
     branch_loc.latitude AS branch_latitude,
     branch_loc.longitude AS branch_longitude,
     branch_loc.city AS branch_city,
     branch_loc.state AS branch_state,
     sp.provider_id,
     sp.name AS provider_name,
     sp.rating,
     sp.image_url,
     sp.business_summary,
     sp.gender_type,
     sp.timings,
     sp.working_hours,
     s.service_name,
     s.service_id,
     ps.price,
     st.service_type_id,
     {haversine_formula} AS distance_km,  -- Calculate distance in kilometers between provider and branch
     TRUE AS verified , 
     CONCAT(COUNT(CASE WHEN rv.status = 1 THEN rv.review_id END), ' reviews') AS review_count,
     ROUND(CAST(AVG(CASE WHEN rv.status = 1 THEN rv.rating END) AS numeric), 1) AS average_rating,
     '1234' AS otp, 
     s.service_name AS all_services
 FROM 
     Branches br
 JOIN ServiceProviders sp ON br.provider_id = sp.provider_id  
 JOIN 
     beautyapp_serviceprovidertype ps ON br.branch_id = ps.branch_id
 JOIN 
     beautyapp_Services s ON ps.service_id_id = s.service_id
 LEFT JOIN 
     Locations branch_loc ON br.location_id = branch_loc.location_id
 LEFT JOIN 
     beautyapp_servicetypes st ON sp.service_type_id = st.service_type_id
 LEFT JOIN 
     beautyapp_review rv ON sp.provider_id = rv.provider_id
     """
     
     # Add WHERE clause with mandatory filters
     if service_id is not None and int(service_id) != 0:
        # print(service_id)
        # print(5454545)
        query += "WHERE s.service_id = %s AND sp.available_credits > 1000 "     
     else:
        query += "WHERE s.category_id = %s AND sp.available_credits > 1000 "
     
     # Exclude service_type_id filter if it's 3
     if service_type_id and int(service_type_id) != 3:
        query += "AND st.service_type_id = %s "
     
     # Add optional filter for category_id if provided
     #if category_id:
         #query += " AND s.category_id = %s "


     query += """ 
     AND ps.status = 'Active'  -- Only include active services
     AND ps.is_deleted = False  
     AND branch_loc.latitude IS NOT NULL AND branch_loc.longitude IS NOT NULL
     AND br.service_status = 1  -- Only include providers whose branch is online
     AND sp.status = 'Active'  -- Only include active service providers
     AND sp.is_deleted = False  -- Exclude deleted providers
     """
 
     query += f""" 
     GROUP BY 
     br.branch_id, br.branch_name, 
     branch_loc.latitude, branch_loc.longitude, branch_loc.city, branch_loc.state, 
     sp.provider_id, sp.name, sp.rating, sp.image_url, sp.business_summary,
     sp.gender_type, sp.timings,sp.working_hours,s.service_name, s.service_id, ps.price,
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


     # Add service_type_id filter if it’s not 3
     if service_type_id and int(service_type_id) != 3:
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
     
         # Handle the average_rating field
         if 'average_rating' in row_dict:
             if row_dict['average_rating'] is not None:
                 row_dict['average_rating'] = round(row_dict['average_rating'], 2)
             else:
                 row_dict['average_rating'] = 0  # or any default value you prefer
         
         # Build the correct image URL using BASE_URL and MEDIA_URL from settings
         image_url = row_dict.get('image_url')
         if image_url:
             row_dict['image_url'] = f"{settings.MEDIA_URL}{image_url}"
     
         data.append(row_dict)

        # Deduplication function
     def get_distinct_results(query_result):
            unique_branch_ids = set()
            distinct_data = []

            for row_dict in query_result:
                branch_id = row_dict.get("branch_id")
                if branch_id not in unique_branch_ids:
                    unique_branch_ids.add(branch_id)
                    distinct_data.append(row_dict)
            
            return distinct_data

        # Call the deduplication function with 'data'
     distinct_data = get_distinct_results(data)

        # Return the distinct result
     #return data
     return distinct_data
         
    #return data

    
     # Method to get provider details
    def get_provider_details(self, provider_id , branch_id):
      query = """
      SELECT 
          sp.provider_id,
          sp.name AS provider_name,
          sp.image_url,
          CASE 
            WHEN sp.service_type_id = 1 THEN 'Salon Service'
            WHEN sp.service_type_id = 2 THEN 'Home Service'
            END AS service_type,
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
          Branches br ON sp.provider_id = br.provider_id
      LEFT JOIN 
          Locations branch_loc ON br.location_id = branch_loc.location_id
      WHERE 
          sp.provider_id = %s AND br.branch_id = %s
          AND sp.is_deleted = False  -- Ensure the provider is not deleted

      """
      params = [provider_id,branch_id]
      
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
                  row_dict['image_url'] = f"{settings.MEDIA_URL}{image_url}"
  
              # Get reviews, calculate average rating and review count
              rating_query = """
                  SELECT AVG(rating) as average_rating, COUNT(*) as review_count
                  FROM beautyapp_review r
                  WHERE r.provider_id = %s AND r.status = 1
              """
              cursor.execute(rating_query, [provider_id])
              rating_result = cursor.fetchone()
  
              row_dict['average_rating'] = round(rating_result[0], 1) if rating_result[0] else 0
              row_dict['review_count'] = f"{rating_result[1]} reviews" if rating_result[1] else "0 reviews"
    
              data.append(row_dict)
  
      return data


    # Method to get services for the provider
    def get_provider_services(self, provider_id, branch_id ,prioritize_service_id=None, category_id=None, subcategory_id=None):
     query = """
     SELECT DISTINCT
         s.service_name,
         s.service_id,
         s.price,
         s.image,
         s.description,
         s.service_time,
         CASE 
             WHEN s.service_id = %s THEN 0
             ELSE 1
         END AS priority
     FROM 
         Branches br
    LEFT JOIN 
         ServiceProviders sp ON sp.provider_id = br.provider_id
     JOIN 
         beautyapp_serviceprovidertype ps ON br.branch_id = ps.branch_id
     JOIN 
         beautyapp_Services s ON ps.service_id_id = s.service_id
     JOIN 
         Locations loc ON sp.address_id = loc.location_id
     LEFT JOIN 
         Locations branch_loc ON br.location_id = branch_loc.location_id
     WHERE 
         br.branch_id =%s
         AND ps.status = 'Active'  -- Only include active services
         AND ps.is_deleted = False -- Only include services that are not deleted
     """
 
     params = [prioritize_service_id, branch_id]
 
     if category_id and category_id !=0 and category_id !='0':
         query += " AND s.category_id = %s"
         params.append(category_id)
 
     if subcategory_id and subcategory_id !=0 and category_id !='0':
         query += " AND s.subcategory_id = %s"
         params.append(subcategory_id)
 
     query += """
     ORDER BY 
         priority,
         s.service_name ASC
     """
 
     with connection.cursor() as cursor:
         cursor.execute(query, params)
         results = cursor.fetchall()
 
         columns = [col[0] for col in cursor.description]
         data = [dict(zip(columns, row)) for row in results]
 
     # Eliminate duplicates from the results
     seen_service_ids = set()
     unique_data = []
 
     for row in data:
         if row['service_id'] not in seen_service_ids:
             unique_data.append(row)
             seen_service_ids.add(row['service_id'])
 
     # Build the correct image URL
     for row in unique_data:
         image = row.get('image')
         if image:
             row['image'] = f"{settings.MEDIA_URL}{image}"
 
     return unique_data


    
        
    # def get_beauticians_for_provider(self, provider_id , branch_id):
    #   role_id = 5  # Define the role_id directly
    # #   query = """
    # #   SELECT 
    # #       s.staff AS beautician_id,
    # #       s.name AS beautician_name,
    # #       s.role_id,
    # #       s.years_of_experience,
    # #       sp.rating,
    # #       sp.image_url AS profile_image
    # #   FROM 
    # #       beautyapp_staff s
    # #   JOIN 
    # #       serviceproviders sp ON s.provider_id = sp.provider_id
    # #   WHERE 
    # #       s.provider_id = %s AND s.role_id = %s
    # #   """
    #   query = """
    #     SELECT 
    #         s.staff AS beautician_id,
    #         s.name AS beautician_name,
    #         s.role_id,
    #         s.years_of_experience,
    #         sp.rating,
    #         sp.image_url AS profile_image
    #     FROM 
    #         beautyapp_staff s
    #     JOIN 
    #         branches br ON br.branch_id = br.branch_id
    #     LEFT JOIN 
    #     serviceproviders sp ON s.provider_id = sp.provider_id
    #     WHERE 
    #         br.branch_id = %s AND s.role_id = %s
    #     """
    #   params = [branch_id, role_id]
    #   with connection.cursor() as cursor:
    #       cursor.execute(query, params)
    #       results = cursor.fetchall()
  
    #       columns = [col[0] for col in cursor.description]
    #       # Prepare the result by zipping columns with row data
    #       data = [dict(zip(columns, row)) for row in results]
  
    #   # Build the correct image URL using BASE_URL and MEDIA_URL from settings
    #   for row in data:
    #       profile_image = row.get('profile_image')
    #       if profile_image:
    #           row['profile_image'] = f"{settings.MEDIA_URL}{profile_image}"
  
    #   return data
    def get_beauticians_for_provider(self, provider_id, branch_id):
     role_id = 5  # Stylist role ID
 
     query = """
         SELECT 
             s.staff AS beautician_id,
             s.name AS beautician_name,
             s.role_id,
             s.years_of_experience,
             sp.rating,
             sp.image_url AS profile_image
         FROM 
             beautyapp_staff s
         JOIN 
             branches br ON s.provider_id = br.provider_id  -- Ensure provider ID matches
         LEFT JOIN 
             serviceproviders sp ON s.provider_id = sp.provider_id
         WHERE 
             br.branch_id = %s AND s.provider_id = %s AND s.role_id = %s
     """
     
     params = [branch_id, provider_id, role_id]
     
     with connection.cursor() as cursor:
         cursor.execute(query, params)
         results = cursor.fetchall()
 
         columns = [col[0] for col in cursor.description]
         data = [dict(zip(columns, row)) for row in results]
 
     # Format profile image URL
     for row in data:
         profile_image = row.get('profile_image')
         if profile_image:
             row['profile_image'] = f"{settings.MEDIA_URL}{profile_image}"
 
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
                row['image'] = f"{settings.MEDIA_URL}{image_url}"

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

            if provider.service_type_id == 1:

                business_summary = f"Established on: {str(provider.established_on)}  Facilities: {str(provider.salon_facilities)}"
            else:
                business_summary = f"Having {str(provider.years_of_experience)} years of experience  Languages Spoken: {str(provider.languages_spoken)}  Travel Capability: {str(provider.travel_capability_kms)} km"


                        # Extract compact working hours only if valid format
            working_hours = provider.working_hours.strip() if provider.working_hours else ""
            # print("working_hours:", working_hours)
            # print("provider.working_hours:", provider.working_hours)

            strict_pattern = r"^\d{2}:\d{2} - \d{2}:\d{2}$"  # Strictly "HH:MM - HH:MM"

            if re.match(strict_pattern, working_hours):
                # print('Yes')
                # Split start and end times
                start_time, end_time = [t.strip() for t in working_hours.split(" - ")]

                # Convert to AM/PM format
                start_time_am_pm = datetime.strptime(start_time, "%H:%M").strftime("%I:%M %p")
                end_time_am_pm = datetime.strptime(end_time, "%H:%M").strftime("%I:%M %p")

                # Remove leading zero from hour if present (e.g., "09:00 AM" -> "9:00 AM")
                start_time_am_pm = start_time_am_pm.lstrip("0")
                end_time_am_pm = end_time_am_pm.lstrip("0")

                # Generate JSON for all days
                working_hours_str = {
                    "Mon": f"{start_time_am_pm},{end_time_am_pm}",
                    "Tue": f"{start_time_am_pm},{end_time_am_pm}",
                    "Wed": f"{start_time_am_pm},{end_time_am_pm}",
                    "Thu": f"{start_time_am_pm},{end_time_am_pm}",
                    "Fri": f"{start_time_am_pm},{end_time_am_pm}",
                    "Sat": f"{start_time_am_pm},{end_time_am_pm}",
                    "Sun": f"{start_time_am_pm},{end_time_am_pm}",
                }

            else:
                print('No')
                working_hours_str = {
                    "Mon": "N/A",
                    "Tue": "N/A",
                    "Wed": "N/A",
                    "Thu": "N/A",
                    "Fri": "N/A",
                    "Sat": "N/A",
                    "Sun": "N/A",
                }

            # print('working_hours_str:', working_hours_str)

            overview_data = {   
                'business_summary': business_summary,
                'gender_type': provider.gender_type,
                'timings': provider.timings,
                'Working_hours':working_hours_str,
                'latitude': provider.address.latitude,
                'longitude': provider.address.longitude
            }
            return overview_data
        except ServiceProvider.DoesNotExist:
            return None
    
    def get_reviews_by_provider(self, provider_id):
      query = """
          SELECT 
              CASE 
                  WHEN r.user_id IS NULL OR u.user_id IS NULL THEN 'Anonymous' 
                  ELSE u.name 
              END as user_name,
              r.review_id, 
              r.rating, 
              r.comment,
              r.created_at,
              r.status  -- Add the status field
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


    
    def get_provider_packages(self, provider_id=1, branch_id=1, service_type=1):
      query = """
      SELECT 
          ps.provider_service_id AS service_id,
          ps.service_type,   -- Ensure service_type is retrieved from the correct table
          ps.price AS service_price,
          ps.status,
          ps.package_services,
          ps.package_name
      FROM 
          beautyapp_serviceprovidertype ps
      WHERE 
          ps.provider_id_id = %s
          AND ps.branch_id = %s
          AND ps.service_type = %s  -- Ensure service_type is filtered correctly
          AND (ps.is_deleted = false OR ps.is_deleted IS NULL)
          AND (ps.status = 'Active' OR ps.status IS NULL)
      """
  
      data = []
  
      try:
          with connection.cursor() as cursor:
              cursor.execute(query, [provider_id, branch_id, service_type])
              results = cursor.fetchall()
  
              if results:
                  columns = [col[0] for col in cursor.description]
  
                  for row in results:
                      row_dict = dict(zip(columns, row))
  
                      # Handle package_services as a list
                      package_services = row_dict.get('package_services')
                      row_dict['package_services'] = package_services.split(', ') if package_services else []
  
                      # Assign package_name if missing
                      row_dict['package_name'] = row_dict.get('package_name') or "Default Package Name"
  
                      data.append(row_dict)
  
      except Exception as e:
          return {
              "status": "failure",
              "message": "Failed to retrieve service provider packages",
              "error": str(e),
              "data": []
          }
  
      return data





    def get_frequently_used_services(self,provider_id , branch_id):
        # Query to extract and count service usage based on appointments
        query = """
        SELECT 
            unnest(string_to_array(service_id_new, ','))::int AS service_id,
            COUNT(*) AS usage_count
        FROM 
            beautyapp_appointment
        WHERE 
            service_id_new IS NOT NULL AND branch_id = %s
        GROUP BY 
            service_id
        ORDER BY 
            usage_count DESC
        LIMIT 3
        """
        with connection.cursor() as cursor:
            cursor.execute(query , [branch_id])
            top_services = cursor.fetchall()

        if not top_services:
            return {
                "status": "success",
                "message": "No frequently used services.",
                "data": []
            }

        # Extract top service IDs
        top_service_ids = [row[0] for row in top_services]

        # Fetch details of the top services
        service_query = """
        SELECT 
            s.service_id,
            s.service_name,
            s.price,
            s.image,
            c.category_name
        FROM 
            beautyapp_services s
        LEFT JOIN 
            beautyapp_category c ON s.category_id = c.category_id
        WHERE 
            s.service_id IN %s
        """
        params = [tuple(top_service_ids)]

        with connection.cursor() as cursor:
            cursor.execute(service_query, params)
            service_results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        # Format the results
        data = []
        for row in service_results:
            row_dict = dict(zip(columns, row))

            # Append base URL to service_image if it exists
            service_image = row_dict.get('image')
            if service_image:
                row_dict['image'] = f"{settings.MEDIA_URL}{service_image}"

            data.append(row_dict)

        return {
            "status": "success",
            "message": "Frequently used services fetched successfully.",
            "data": data
        }

   
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
    message = models.CharField(max_length=255, null=True, blank=True)  
    stylist = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True, default=None) 
    used_credits = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    reason = models.CharField(max_length=255, null=True, blank=True) 
    reference_image = models.ImageField(upload_to='references_images/',storage=AzureMediaStorage(), null=True, blank=True)
 
 
    
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
    review_id = models.AutoField(primary_key=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    comment = models.TextField()
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')  
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        choices=[(0, 'Inactive'), (1, 'Active')],
        null=True,  
        blank=True,  
    )
class Meta:
        managed = False
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

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)  
    text = models.CharField(max_length=255)        
    type = models.CharField(max_length=50)   

    class Meta:
        managed=False
        db_table = 'messages'       

    def __str__(self):
        return self.text


class CallbackRequest(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    created_date = models.DateField(default=now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=[(0, 'Inactive'), (1, 'Active')], default=1)

    class Meta:
        db_table = 'callbackrequest'

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'newsletter'  

    def __str__(self):
        return self.email

class ContactForm(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'beautyapp_contact' 

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=255)
    status = models.BooleanField(default=True)


    class Meta:
        managed=False
        db_table = 'provider_roles'

    def __str__(self):
        return self.role_name
    
