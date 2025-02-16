from rest_framework import serializers,status
from .models import ServiceProvider,ProviderBankDetails,ProviderTaxRegistration,Locations,Role,Staff,Branches,Review,User,Category,Subcategory,Services,Serviceprovidertype,Permissions,Status
from rest_framework.views import APIView
from rest_framework.response import Response





class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = '__all__'

class ServiceProvidersSerializer(serializers.ModelSerializer):
    
    location = serializers.CharField(write_only=True) 
    provider_id = serializers.IntegerField(read_only=True)  

    class Meta:
        model = ServiceProvider
        fields = ['provider_id', 'name', 'email', 'phone', 'service_type', 'location']
        extra_kwargs = {
            'email': {'required': True},
            'phone': {'required': True},
            #'location': {'required': True},
            'location': {'required': True},
            'service_type': {'required': True},
        }

    def create(self, validated_data):
        # Extract city from validated_data
        location_name = validated_data.pop('location')
        service_provider = None

        # Check if address_id is NULL in ServiceProvider
        address_id = validated_data.get('address_id')

        if address_id:
            # If address_id exists, update the corresponding Locations record
            location = Locations.objects.filter(location_id=address_id.pk).first()
            if location:
                location.city = location_name  # Update city
                location.save()
            else:
                raise serializers.ValidationError("Invalid address_id. No matching location found.")
        else:
            # If address_id is NULL, insert a new record into Locations
            location = Locations.objects.create(
                city=location_name,
                address_line1='',
                address_line2='',
                state='',
                postal_code=0,
                country='',
                latitude=0.0,
                longitude=0.0,
            )
            validated_data['address_id'] = location.location_id   

        # Create the ServiceProvider instance
        service_provider = ServiceProvider.objects.create(**validated_data)
        return service_provider
        
class SalonDetailsSerializer(serializers.ModelSerializer):
    saloon_location = serializers.CharField(write_only=True) 
    saloon_address = serializers.CharField(write_only=True) 
    print(saloon_address , saloon_location)
    class Meta:
        model = ServiceProvider
        fields = [
            'owner_name', 'established_on','email', 'phone','saloon_location','saloon_address','name','services_offered', 'staff_information','salon_facilities', 'cancellation_policy','working_hours'
        ]

    def validate(self, data):
        print(8541259874)
        # Check for required fields regardless of whether the update is partial or not
        required_fields = ['owner_name', 'email', 'phone','name']
        for field in required_fields:
            if field not in data or not data[field]:
                # If the field is not provided or is empty, check if it exists in the current instance
                if not getattr(self.instance, field, None):
                    raise serializers.ValidationError({field: f"{field} is required."})
                
        #print(data)
        return data
    def update(self, instance, validated_data):
        # Extract city from validated_data
        #print(1234577)
        saloon_location = validated_data.pop('saloon_location')
        saloon_address= validated_data.pop('saloon_address')
        service_provider = None

        # Check if address_id is NULL in ServiceProvider
        address_id = instance.address_id

        if address_id:
            # Update the location if address_id is provided
            try:
                location = Locations.objects.get(location_id=address_id)
                location.city = saloon_location  # Update city
                location.address_line1 = saloon_address  # Update address_line1
                location.save()  # Save updated location

                #print(f"Updating location: {location.location_id} - City: {saloon_location}, Address: {saloon_address}")


            except Locations.DoesNotExist:
                raise serializers.ValidationError("Invalid address_id. No matching location found.")
        else:
            # If no address_id is provided, create a new location record
            location = Locations.objects.create(
                city=saloon_location,
                address_line1=saloon_address,
                address_line2="",
                state="",
                postal_code=0,
                country="",
                latitude=0.0,
                longitude=0.0
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()

        # Create the service provider with the new location
        # service_provider = ServiceProvider.objects.create(
        #     **validated_data,
        #     address_id=location.location_id  # Link the newly created or updated location
        # )

        #print(f"Updating location 1234 : {location.location_id} - City 1 : {saloon_location}, Address 1: {saloon_address}")
    
        return instance


class FreelancerDetailsSerializer(serializers.ModelSerializer):
    
    freelancer_location = serializers.CharField(write_only=True) 
    home_address = serializers.CharField(write_only=True) 
    class Meta:
        model = ServiceProvider
        fields = [
            'owner_name','years_of_experience','email', 'phone','freelancer_location','home_address','languages_spoken', 'travel_capability_kms', 'services_offered',
            'certifications', 'willing_to_work_holidays','available_slots'
        ]

    def validate(self, data):
        # Check for required fields regardless of whether the update is partial or not
        required_fields = ['home_address', 'email', 'phone', 'owner_name','freelancer_location']
        for field in required_fields:
            if field not in data or not data[field]:
                # If the field is not provided or is empty, check if it exists in the current instance
                if not getattr(self.instance, field, None):
                    raise serializers.ValidationError({field: f"{field} is required."})
        return data
    def update(self, instance, validated_data):
        # Extract city from validated_data
        #print(1234577)
        freelancer_location = validated_data.pop('freelancer_location')
        home_address= validated_data.pop('home_address')
        service_provider = None

        # Check if address_id is NULL in ServiceProvider
        address_id = instance.address_id

        if address_id:
            # Update the location if address_id is provided
            try:
                location = Locations.objects.get(location_id=address_id)
                location.city = freelancer_location  # Update city
                location.address_line1 = home_address  # Update address_line1
                location.save()  # Save updated location

                #print(f"Updating location: {location.location_id} - City: {saloon_location}, Address: {saloon_address}")


            except Locations.DoesNotExist:
                raise serializers.ValidationError("Invalid address_id. No matching location found.")
        else:
            # If no address_id is provided, create a new location record
            location = Locations.objects.create(
                city=freelancer_location,
                address_line1=home_address,
                address_line2="",
                state="",
                postal_code=0,
                country="",
                latitude=0.0,
                longitude=0.0
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()

        # Create the service provider with the new location
        # service_provider = ServiceProvider.objects.create(
        #     **validated_data,
        #     address_id=location.location_id  # Link the newly created or updated location
        # )

        #print(f"Updating location 1234 : {location.location_id} - City 1 : {saloon_location}, Address 1: {saloon_address}")
    
        return instance



class ProviderBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderBankDetails
        fields = '__all__'

    def validate_provider_id(self, value):
        # Check if the provider_id exists in ServiceProvider
        if not ServiceProvider.objects.filter(provider_id=value).exists():
            raise serializers.ValidationError("Invalid provider_id. No matching service provider found.")
        return value

class ProviderTaxRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderTaxRegistration
        fields = ['provider', 'tax_identification_number', 'tax_file', 'gst_number', 'gst_file', 'proof_of_identity_type', 'proof_of_identity_number', 'identity_file', 'proof_of_address_type', 'address_file']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_id', 'role_name', 'status']

class StaffSerializer(serializers.ModelSerializer):
    branch_name = serializers.SerializerMethodField()  # Custom field for branch name
    role_name = serializers.SerializerMethodField()  # Custom field for role name

    class Meta:
        model = Staff
        fields = ['staff','name', 'role_name', 'branch_name', 'status','role_id','branch_id']  # Include required fields

    def get_branch_name(self, obj):
        """
        Retrieve the branch name from the ServiceProvider associated with the staff.
        """
        if obj.branch:  # Check if a role exists for this staff member
            return obj.branch.branch_name  # Fetch the role_name from the Role table
        return None  # Return None if no role is assigned

    def get_role_name(self, obj):
        """
        Retrieve the role name from the Role table based on the role_id.
        """
        if obj.role:  # Check if a role exists for this staff member
            return obj.role.role_name  # Fetch the role_name from the Role table
        return None  # Return None if no role is assigned

    
class StaffCreateSerializer(serializers.ModelSerializer):
    branch_id = serializers.IntegerField(write_only=True)  # Add the branch_id as a write-only field
    branch_name = serializers.SerializerMethodField()  # Add a custom field to represent branch_name

    class Meta:
        model = Staff
        fields = ['name', 'role', 'branch_id', 'branch_name', 'photo']  # Include branch_id and branch_name

    def get_branch_name(self, obj):
        # Return branch_name based on branch_id
        if obj.branch:  # Check if branch exists
            return obj.branch.branch_name
        return None  # Return None if no branch associated

    
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branches
        fields = ['branch_id', 'branch_name']  

class BranchesSerializer(serializers.ModelSerializer):
    branch_location = serializers.SerializerMethodField()
    branch_address = serializers.SerializerMethodField()
    location_id = serializers.PrimaryKeyRelatedField(queryset=Locations.objects.all(), source='location', write_only=True)

    class Meta:
        model = Branches
        fields = ['branch_id', 'branch_name', 'phone', 'branch_address', 'branch_location', 'logo', 'location', 'location_id']

    def get_branch_address(self, obj):
        # Retrieve the address from the related Locations model
        return obj.location.address_line1

    def get_branch_location(self, obj):
        # Retrieve the location (city) from the related Locations model
        return obj.location.city


class BranchListSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()

    class Meta:
        model = Branches
        fields = ['branch_id','branch_name', 'phone', 'location', 'logo']

    def get_location(self, obj):
        try:
            # Check if location_id is available and get the related location information
            if obj.location:
                return obj.location.city  # Access the city of the related Location model
            else:
                return None  # Return None if location does not exist
        except AttributeError:
            # In case location is missing or not set, handle the exception
            return None
        
class ReviewSerializer(serializers.ModelSerializer):
    # Fetch the customer name using the user_id relation
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['review_id', 'created_at', 'order_id', 'user_id', 'customer_name', 'rating', 'comment']

    def get_customer_name(self, obj):
        # Get the user instance based on the user_id and return the name
        try:
            user = User.objects.get(user_id=obj.user_id)
            return user.name
        except User.DoesNotExist:
            return None  # Return None if user does not exist       

class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = '__all__'

class ServiceProviderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serviceprovidertype
        fields = '__all__'

class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serviceprovidertype
        fields = ['service_id', 'provider_id', 'branch', 'price', 'duration', 'status']

class ServiceSerializer(serializers.ModelSerializer):
    provider_details = ServiceProviderSerializer(many=True, read_only=True)

    class Meta:
        model = Services
        fields = ['service_id', 'service_name', 'category', 'subcategory', 'sku_value', 'service_time', 'provider_details']


class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permissions
        fields = '__all__'

class CreatePermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permissions
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['status_id', 'status_name']


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = '__all__'

class ServiceprovidertypeSerializer(serializers.ModelSerializer):
   class Meta:
        model = Serviceprovidertype
        fields = '__all__'