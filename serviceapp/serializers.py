from rest_framework import serializers,status
from .models import ServiceProvider,ProviderBankDetails,ProviderTaxRegistration,Locations,Role,Staff,Branches,Review,User,Category,Subcategory,Services,Serviceprovidertype,Permissions,Status,Beautician,ProviderTransactions,AdminUser,Appointment,Coupon
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, date




class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = '__all__'

class ServiceProvidersSerializer(serializers.ModelSerializer):
    location = serializers.CharField(write_only=True)
    latitude = serializers.FloatField(required=False, allow_null=True, write_only=True)
    longitude = serializers.FloatField(required=False, allow_null=True, write_only=True)
    provider_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ServiceProvider
        fields = [
            'provider_id', 'name', 'email', 'phone', 'service_type',
            'location', 'latitude', 'longitude'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'phone': {'required': True},
            'location': {'required': True},
            'service_type': {'required': True},
        }

    def create(self, validated_data):
     location_name = validated_data.pop('location')
     latitude = validated_data.pop('latitude', None)
     longitude = validated_data.pop('longitude', None)
 
     # Try to get an existing location
     location = Locations.objects.filter(city=location_name).first()
 
     # If no location exists, create one
     if not location:
         location = Locations.objects.create(
             city=location_name,
             address_line1='',
             address_line2='',
             state='',
             postal_code=0,
             country='',
             latitude=latitude if latitude is not None else 0.0,
             longitude=longitude if longitude is not None else 0.0,
         )
 
     # Try to get an existing branch
     branch = Branches.objects.filter(location=location).first()
 
     # If no branch exists, create one
     if not branch:
         branch = Branches.objects.create(
             location=location,
             branch_name=f'Default Branch for {location_name}'
         )
 
     # Assign the branch and address ID
     validated_data['branch'] = branch
     validated_data['address_id'] = location.location_id  
 
     # Create the ServiceProvider instance
     return ServiceProvider.objects.create(**validated_data)


        
class SalonDetailsSerializer(serializers.ModelSerializer):
    saloon_location = serializers.CharField(write_only=True) 
    saloon_address = serializers.CharField(write_only=True) 
    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)

    print(saloon_address , saloon_location)
    class Meta:
        model = ServiceProvider
        fields = [
            'owner_name', 'established_on','email', 'phone','saloon_location','saloon_address','latitude', 'longitude','name','services_offered', 'staff_information','salon_facilities', 'cancellation_policy','working_hours'
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
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)

        service_provider = None

        # Check if address_id is NULL in ServiceProvider
        address_id = instance.address_id

        if address_id:
            # Update the location if address_id is provided
            try:
                location = Locations.objects.get(location_id=address_id)
                location.city = saloon_location if saloon_location else location.city  # Update city
                location.address_line1 = saloon_address if saloon_address else location.address_line1  # Update address_line1
                if latitude is not None:
                    location.latitude = latitude  # Update latitude
                if longitude is not None:
                    location.longitude = longitude  # Update longitude
                location.save()  # Save updated location

            except Locations.DoesNotExist:
                raise serializers.ValidationError("Invalid address_id. No matching location found.")

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
                latitude=latitude if latitude is not None else 0.0,
                longitude=longitude if longitude is not None else 0.0
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
    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ServiceProvider
        fields = [
            'owner_name','years_of_experience','email', 'phone','freelancer_location','latitude', 'longitude','home_address','languages_spoken', 'travel_capability_kms', 'services_offered',
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
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        service_provider = None

        # Check if address_id is NULL in ServiceProvider
        address_id = instance.address_id

        if address_id:
            try:
                location = Locations.objects.get(location_id=address_id)
                location.city = freelancer_location
                location.address_line1 = home_address
                if latitude is not None:
                    location.latitude = latitude
                if longitude is not None:
                    location.longitude = longitude
                location.save()
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
                latitude=latitude if latitude is not None else 0.0,
                longitude=longitude if longitude is not None else 0.0
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
    tax_file = serializers.FileField(required=False, allow_null=True)
    gst_file = serializers.FileField(required=False, allow_null=True)
    identity_file = serializers.FileField(required=False, allow_null=True)
    address_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = ProviderTaxRegistration
        fields = [
            'provider', 'tax_identification_number', 'tax_file',
            'gst_number', 'gst_file', 'proof_of_identity_type',
            'proof_of_identity_number', 'identity_file',
            'proof_of_address_type', 'address_file'
        ]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_id', 'role_name', 'status']

class StaffSerializer(serializers.ModelSerializer):
    branch_name = serializers.SerializerMethodField()  # Custom field for branch name
    role_name = serializers.SerializerMethodField()  # Custom field for role name

    class Meta:
        model = Staff
        fields = ['staff','name', 'role_name', 'branch_name', 'status','role_id','branch_id','phone']  # Include required fields

    def get_branch_name(self, obj):
        """
        Retrieve the branch name from the ServiceProvider associated with the staff.
        """
        if obj.branch:  # Check if a branch exists for this staff member
            return obj.branch.branch_name  # Fetch the branch name from the Branch table
        return None  # Return None if no branch is assigned

    def get_role_name(self, obj):
        """
        Retrieve the role name from the Role table based on the role_id.
        """
        try:
            if obj.role:  # Check if a role exists for this staff member
                return obj.role.role_name  # Fetch the role_name from the Role table
        except Role.DoesNotExist:
            return None  # Return None if no role is assigned or the role doesn't exist
        return None  # Return None if no role is assigned


    
class StaffCreateSerializer(serializers.ModelSerializer):
    branch_id = serializers.IntegerField(write_only=True)  # Add branch_id as a write-only field
    branch_name = serializers.SerializerMethodField()  # Add branch_name as a custom field

    class Meta:
        model = Staff
        fields = ['name', 'role', 'branch_id', 'branch_name', 'photo', 'provider_id', 'phone']  # Exclude 'status'

    def get_branch_name(self, obj):
        # Return branch_name based on branch_id
        return obj.branch.branch_name if obj.branch else None  # Return None if no branch associated

    def validate_phone(self, value):
        """
        Validate that the phone number is unique.
        """
        if Staff.objects.filter(phone=value, is_deleted=False).exists():
            raise serializers.ValidationError("This phone number is already in exist.")
        return value

    def create(self, validated_data):
        branch_id = validated_data.pop('branch_id')  # Remove branch_id from validated data
        try:
            # Look up the branch instance
            branch = Branches.objects.get(branch_id=branch_id)
            validated_data['branch'] = branch  # Set the branch instance
            validated_data['provider_id'] = branch.provider_id  # Get the provider_id from the branch
        except Branches.DoesNotExist:
            raise serializers.ValidationError({"branch_id": "Invalid branch ID. Branch not found."})

        # Set the default status to "Active" if it is not explicitly provided
        validated_data.setdefault('status', 'Active')

        # Create and return the Staff instance
        return Staff.objects.create(**validated_data)



    
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branches
        fields = ['branch_id', 'branch_name']  

class BranchesSerializer(serializers.ModelSerializer):
    branch_location = serializers.SerializerMethodField()
    branch_address = serializers.SerializerMethodField()
    location_id = serializers.PrimaryKeyRelatedField(queryset=Locations.objects.all(), source='location', write_only=True, required=False, allow_null=True)
    provider_id = serializers.PrimaryKeyRelatedField(queryset=ServiceProvider.objects.all(), source='provider', write_only=True, required=True)

    class Meta:
        model = Branches
        fields = ['branch_id', 'branch_name', 'phone', 'branch_address', 'branch_location', 'logo', 'location', 'location_id', 'provider_id']

    def get_branch_address(self, obj):
        # Retrieve the address from the related Locations model
        return obj.location.address_line1

    def get_branch_location(self, obj):
        # Retrieve the location (city) from the related Locations model
        return obj.location.city


class BranchListSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    provider_id = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Branches
        fields = ['branch_id', 'branch_name', 'phone', 'location', 'latitude', 'longitude', 'logo', 'provider_id']

    def get_location(self, obj):
        try:
            if obj.location:
                return obj.location.city  # Return city name
            return None
        except AttributeError:
            return None

    def get_provider_id(self, obj):
        try:
            if obj.provider:
                return obj.provider.provider_id
            return None
        except AttributeError:
            return None

    def get_latitude(self, obj):
        try:
            if obj.location and obj.location.latitude is not None:
                return obj.location.latitude
            return None
        except AttributeError:
            return None

    def get_longitude(self, obj):
        try:
            if obj.location and obj.location.longitude is not None:
                return obj.location.longitude
            return None
        except AttributeError:
            return None


        
class ReviewSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    service_objects = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "review_id",
            "created_at",
            "created_at_formatted",  # Ensure this is included
            "order_id",
            "user_id",
            "customer_name",
            "rating",
            "comment",
            "service_objects",
            "status"
        ]

    def get_customer_name(self, obj):
        try:
            user = User.objects.get(user_id=obj.user_id)
            return user.name
        except User.DoesNotExist:
            return None

    def get_service_objects(self, obj):
        return obj.service_objects if hasattr(obj, 'service_objects') else []   

    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%d %B %Y") if obj.created_at else None   

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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'

class BeauticianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beautician
        fields = '__all__'

class ProviderTransactionSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = ProviderTransactions
        fields = ['id', 'date', 'amount', 'type', 'payment_type', 'transaction_id']

    def get_amount(self, obj):
        return f"Rs. {int(obj.amount)}"

    def get_date(self, obj):
        if isinstance(obj.date, (datetime, date)):
            return obj.date.strftime("%d %b %Y")
        elif isinstance(obj.date, str):
            # Parse the string to a date object assuming the format is "DD-MM-YYYY"
            parsed_date = datetime.strptime(obj.date, "%d-%m-%Y").date()
            return parsed_date.strftime("%d %b %Y")
        return obj.date  # Return as is if it's neither date nor a correctly formatted string
    

class ReviewStatusSerializer(serializers.Serializer):
    review_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=[(0, 'Inactive'), (1, 'Active')])

class AddPackageServiceSerializer(serializers.ModelSerializer):
    selected_service_ids = serializers.CharField(  # Accept as a string
        write_only=True,
        required=False  
    )
    package_name = serializers.CharField(
        write_only=True,
        required=False  
    )
    branch_id = serializers.IntegerField(write_only=True, required=False)  
    status = serializers.CharField(
        write_only=True,
        required=False,
        default='Active'
    )

    class Meta:
        model = Services
        fields = [
            'price',
            'status',
            'provider',
            'package_services',
            'selected_service_ids',
            'package_name',
            'branch_id',
            'package_services_ids',  # Add the new field
        ]

    def create(self, validated_data):
        selected_service_ids = validated_data.pop('selected_service_ids', None)
        package_name = validated_data.pop('package_name', None)
        branch_id = validated_data.pop('branch_id', None)
        provider = validated_data.get('provider')

        selected_service_ids_list = []
        if selected_service_ids:
            try:
                selected_service_ids_list = [int(service_id.strip()) for service_id in selected_service_ids.split(',')]
            except ValueError:
                raise serializers.ValidationError({"selected_service_ids": "Service IDs must be a comma-separated list of integers."})

            # Retrieve service names from the database
            service_names = Services.objects.filter(service_id__in=selected_service_ids_list).values_list('service_name', flat=True)
            validated_data['package_services'] = ', '.join(service_names)

        if package_name:
            validated_data['service_name'] = package_name

        if branch_id:
            try:
                Branches.objects.get(branch_id=branch_id)
                validated_data['branch_id'] = branch_id
            except Branches.DoesNotExist:
                raise serializers.ValidationError({"branch_id": "Invalid branch ID."})

        validated_data['service_type'] = 1  

        existing_instance = Services.objects.filter(
            provider=provider,
            service_name=package_name,
            branch_id=branch_id
        ).first()

        if existing_instance:
            for key, value in validated_data.items():
                setattr(existing_instance, key, value)
            existing_instance.package_services_ids = ', '.join(map(str, selected_service_ids_list))  # Store IDs
            existing_instance.save()
            return existing_instance

        validated_data['package_services_ids'] = ', '.join(map(str, selected_service_ids_list))
        return Services.objects.create(**validated_data)


    def update(self, instance, validated_data):
        # Update logic for existing instances
        if 'package_name' in validated_data:
            instance.service_name = validated_data.pop('package_name')

        if 'branch_id' in validated_data:
            branch_id = validated_data.pop('branch_id')
            try:
                Branches.objects.get(branch_id=branch_id)
                instance.branch_id = branch_id
            except Branches.DoesNotExist:
                raise serializers.ValidationError({"branch_id": "Invalid branch ID."})

        if 'selected_service_ids' in validated_data:
            selected_service_ids = validated_data.pop('selected_service_ids')
            try:
                selected_service_ids_list = [int(service_id.strip()) for service_id in selected_service_ids.split(',')]
            except ValueError:
                raise serializers.ValidationError({"selected_service_ids": "Service IDs must be a comma-separated list of integers."})

            service_names = Services.objects.filter(service_id__in=selected_service_ids_list).values_list('service_name', flat=True)
            instance.package_services = ', '.join(service_names)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        # After updating the instance, store the updated `package_services_ids`
        if 'selected_service_ids' in validated_data:
            instance.package_services_ids = ', '.join(map(str, selected_service_ids_list))

        instance.save()
        return instance

    def to_representation(self, instance):
        """Ensure all required details are included in the response."""
        data = super().to_representation(instance)
        data['service_id'] = instance.service_id
        data['package_name'] = instance.service_name  
        data['branch_id'] = instance.branch_id  
        return data





class PackagesSerializer(serializers.ModelSerializer):
    package_id = serializers.IntegerField(source='service_id')  # Alias service_id as package_id
    package_name = serializers.CharField(source='service_name')  # Alias service_name as package_name
    package_services = serializers.CharField()  # Assuming this is stored as a comma-separated string
    price = serializers.DecimalField(max_digits=10, decimal_places=2)  # Assuming price is a decimal field
    status = serializers.CharField()  # Assuming status is a char field
    is_deleted = serializers.BooleanField()  # Assuming is_deleted is a boolean field

    class Meta:
        model = Services
        fields = ['package_id', 'package_name', 'package_services', 'price', 'status', 'is_deleted']


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ['username', 'email', 'phone_number', 'role', 'otp', 'otp_created_at', 'last_login', 'token']

class ProviderDetailsSerializer(serializers.ModelSerializer):
    bank_details = serializers.SerializerMethodField()
    tax_details = serializers.SerializerMethodField()
    branch = serializers.CharField(source='branch.location.city', read_only=True)
    address = serializers.CharField(source='branch.location.address_line1', read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = ServiceProvider
        fields = [
            'owner_name', 'name', 'phone', 'email', 'branch', 'address',
            'established_on', 'services_offered', 'working_hours', 'cancellation_policy',
            'staff_information', 'image_url', 'business_summary', 'gender_type', 'timings',
            'salon_facilities', 'years_of_experience', 'languages_spoken', 'travel_capability_kms',
            'certifications', 'willing_to_work_holidays', 'bank_details', 'tax_details',
            'latitude', 'longitude'
        ]

    def get_bank_details(self, obj):
        bank_details = ProviderBankDetails.objects.filter(provider=obj)
        return [
            {
                'bank_id': bank.id,
                'account_holder_name': bank.account_holder_name,
                'bank_name': bank.bank_name,
                'bank_account_number': bank.bank_account_number,
                'account_type': bank.account_type,
                'bank_branch': bank.bank_branch,
                'ifsc_code': bank.ifsc_code
            }
            for bank in bank_details
        ]

    def get_tax_details(self, obj):
        tax_details = ProviderTaxRegistration.objects.filter(provider=obj)
        return [
            {
                'tax_id': tax.id,
                'tax_identification_number': tax.tax_identification_number,
                'tax_file': tax.tax_file.url if tax.tax_file else None,
                'gst_number': tax.gst_number,
                'gst_file': tax.gst_file.url if tax.gst_file else None,
                'proof_of_identity_type': tax.proof_of_identity_type,
                'proof_of_identity_number': tax.proof_of_identity_number,
                'identity_file': tax.identity_file.url if tax.identity_file else None,
                'proof_of_address_type': tax.proof_of_address_type,
                'address_file': tax.address_file.url if tax.address_file else None
            }
            for tax in tax_details
        ]

    def get_latitude(self, obj):
        branch = Branches.objects.filter(provider=obj, is_deleted=False).first()
        return branch.location.latitude if branch and branch.location else None

    def get_longitude(self, obj):
        branch = Branches.objects.filter(provider=obj, is_deleted=False).first()
        return branch.location.longitude if branch and branch.location else None
    
class AppointmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name')
    user_phone = serializers.CharField(source='user.phone')
    service_names = serializers.SerializerMethodField()
    branch_city = serializers.SerializerMethodField()
    appointment_date = serializers.SerializerMethodField()
    appointment_time = serializers.SerializerMethodField()
    stylist_name = serializers.SerializerMethodField()
    stylist_id = serializers.SerializerMethodField()
    provider_id = serializers.SerializerMethodField()  # Add provider_id
    provider_name = serializers.SerializerMethodField()  # Add provider_name

    class Meta:
        model = Appointment
        fields = [
            'appointment_id',
            'appointment_date',
            'appointment_time',
            'branch',
            'user_name',
            'user_phone',
            'service_names',
            'branch_city',
            'stylist_name',
            'stylist_id',
            'provider_id',  # Include provider_id
            'provider_name',  # Include provider_name
        ]

    def get_service_names(self, obj):
        service_ids = obj.service_id_new.split(',')
        services = Services.objects.filter(service_id__in=service_ids)
        return [
            {"service_name": service.service_name, "price": float(service.price) if service.price else 0}
            for service in services
        ]

    def get_branch_city(self, obj):
        return obj.branch.location.city if obj.branch and obj.branch.location else None

    def get_appointment_date(self, obj):
        return obj.appointment_date.strftime('%d-%m-%Y')

    def get_appointment_time(self, obj):
        return obj.appointment_time.strftime('%H:%M')

    def get_stylist_name(self, obj):
        if obj.stylist_id:
            try:
                return Beautician.objects.get(id=obj.stylist_id).name
            except Beautician.DoesNotExist:
                return None
        return None

    def get_stylist_id(self, obj):
        return obj.stylist_id if obj.stylist_id else None

    def get_provider_id(self, obj):
        return obj.provider_id if hasattr(obj, 'provider_id') else None  # Ensure the field exists

    def get_provider_name(self, obj):
        if hasattr(obj, 'provider') and obj.provider:
            return obj.provider.name  # Assuming 'provider' is a ForeignKey to a Provider model
        return None

    
class SubcategoriesSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)

    class Meta:
        model = Subcategory
        fields = ['subcategory_id', 'subcategory_name', 'category', 'category_name', 'status', 'is_deleted']

class ServicesSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.subcategory_name', read_only=True)

    class Meta:
        model = Services
        fields = [
            'service_id', 'service_name', 'category', 'category_name', 
            'subcategory', 'subcategory_name', 'price','status','sku_value',"description", 'service_time','is_deleted'
        ]

class CouponSerializer(serializers.ModelSerializer):
    valid_from = serializers.SerializerMethodField()
    valid_until = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    discount_value = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            "id", "coupon_code", "coupon_limit", "valid_from", "valid_until",
            "discount_type", "discount_value", "status", "created_datetime", "provider"
        ]

    def get_valid_from(self, obj):
        return obj.valid_from.strftime("%d %b %Y") if obj.valid_from else None

    def get_valid_until(self, obj):
        return obj.valid_until.strftime("%d %b %Y") if obj.valid_until else None

    def get_status(self, obj):
        """ 
        - Status `1` → "Active" (unless expired)
        - Status `2` → "Inactive"
        - If `status=1` but `valid_until` is in the past → "Expired"
        """
        if obj.status == 1:
            if obj.valid_until and obj.valid_until < datetime.now():
                return "Expired"
            return "Active"
        elif obj.status == 2:
            return "Inactive"
        return "Unknown"

    def get_discount_value(self, obj):
        """ Format discount value based on discount type """
        if obj.discount_type == "Flat":  # Check for "Flat"
            return f"₹{obj.discount_value}"  # Show currency format
        elif obj.discount_type == "Percentage":
            return f"{obj.discount_value}%"
        return str(obj.discount_value)
    
class CouponsSerializer(serializers.ModelSerializer):
    valid_from = serializers.DateTimeField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"], required=False)
    valid_until = serializers.DateTimeField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"], required=False)
    discount_type = serializers.ChoiceField(
        choices=Coupon.DISCOUNT_TYPE_CHOICES, required=False, default="flat"
    )
    discount_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=True
    )

    class Meta:
        model = Coupon
        fields = [
            'coupon_code', 'coupon_limit', 'valid_from',
            'valid_until', 'discount_type', 'discount_value', 'status'
        ]

    def to_representation(self, instance):
        """Customize the response format for discount_value"""
        data = super().to_representation(instance)
        
        # Format `discount_value` in the response based on `discount_type`
        if instance.discount_type.lower() == "flat":
            data['discount_value'] = f"₹{int(instance.discount_value)}"  # Remove decimal places
        elif instance.discount_type.lower() == "percentage":
            data['discount_value'] = f"{int(instance.discount_value)}%"  # Remove decimal places
        
        return data
    
