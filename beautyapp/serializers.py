from rest_framework import serializers,status
from .models import ServiceTypes
from .models import BeautyParlour
from .models import ServiceProvider
from .models import Beautician
from .models import FilterProvider
from .models import Photo
from .models import FAQ
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .models import Staff
from .models import Serviceprovidertype
from .models import Services
from .models import StaffReview
from .models import Appointment
from .models import Payment
from .models import CustomerFeedback
from .models import Category
from .models import Subcategory
from .models import Login
from .models import Review
from .models import Coupon
from .models import ServiceFAQ
from .models import BeautyAppPackage
from .models import Message,CallbackRequest,Newsletter,ContactForm,Branches
from django.conf import settings
from rest_framework import serializers


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = '__all__'
        
class ServiceTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTypes
        fields = '__all__'
        
class BeautyParlourSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = BeautyParlour
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    

class ServiceProviderSerializer(serializers.ModelSerializer):
    # city = serializers.CharField()
    # state = serializers.CharField()

    class Meta:
        model = ServiceProvider
        fields = [
            'provider_id', 'name', 'email', 'phone', 'years_of_experience',
            'skills', 'specializations', 'rating', 'status', 'working_hours',
            'available_slots', 'created_at', 'updated_at', 'image_url',
            'business_summary', 'gender_type', 'timings'
        ]

# class BranchSerializer(serializers.ModelSerializer):
#     provider = ServiceProviderSerializer()  # Nested Serializer
#     city = serializers.CharField(source='location.city')
#     state = serializers.CharField(source='location.state')


#     class Meta:
#         model = Branches
#         fields = ['branch_id', 'branch_name', 'location', 'provider', 'service_status', 'created_at', 'updated_at','city', 'state']
    
class BranchSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source='location.city', allow_null=True)
    state = serializers.CharField(source='location.state', allow_null=True)

    class Meta:
        model = Branches
        fields = ['branch_id', 'branch_name', 'location', 'service_status', 'created_at', 'updated_at', 'city', 'state']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Fetch provider details and merge into response
        if instance.provider:
            provider_data = ServiceProviderSerializer(instance.provider).data
            data.update(provider_data)  # Merge provider details into response
        
        return data



class AvailableSlotsSerializer(serializers.ModelSerializer):
    available_slots = serializers.JSONField()

    class Meta:
        model = ServiceProvider
        fields = ['provider_id', 'available_slots']
        
class FilterProviderSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = FilterProvider
        fields = '__all__'

def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class BeauticianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beautician
        fields = '__all__'

class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = '__all__'

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id','name','email','phone']
        
class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = '__all__'
        

class ServiceprovidertypeSerializer(serializers.ModelSerializer):
   class Meta:
        model = Serviceprovidertype
        fields = '__all__'


class ServiceprovidertypeSerializer2(serializers.ModelSerializer):
   class Meta:
        model = Serviceprovidertype
        fields = '__all__'


class StaffReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffReview
        fields = '__all__'
    
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class CustomerFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerFeedback
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

    def validate_provider(self, value):
        if not ServiceProvider.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("Provider ID does not exist.")
        return value

    def validate_user(self, value):
        if not User.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("User ID does not exist.")
        return value

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class ServiceFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFAQ
        fields = '__all__'


class BeautyAppPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeautyAppPackage
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name')
    user_phone = serializers.CharField(source='user.phone')
    service_names = serializers.SerializerMethodField()
    branch_city = serializers.SerializerMethodField()  # Branch city as a method field
    appointment_date = serializers.SerializerMethodField()
    appointment_time = serializers.SerializerMethodField()
    stylist_name = serializers.SerializerMethodField()  # Add stylist name
    stylist_id = serializers.SerializerMethodField()  # Add stylist_id field
    stylist_photo = serializers.SerializerMethodField()  # Add stylist photo field
    reference_image = serializers.SerializerMethodField() 


    class Meta:
        model = Appointment
        fields = [
            'appointment_id',
            'appointment_date',
            'appointment_time',
            'branch',
            'user_name',
            'user_phone',
            'service_names',  # Array of service names
            'branch_city',
            'stylist_name',  # Add stylist name to fields
            'stylist_id',  # Add stylist_id to fields
            'stylist_photo',  # Include stylist photo
            'reference_image',

        ]

    def get_service_names(self, obj):
        service_ids = obj.service_id_new.split(',')  
        services = Services.objects.filter(service_id__in=service_ids)
        service_details = [
            {"service_name": service.service_name, "price": float(service.price) if service.price else 0}
            for service in services
        ]
        return service_details  

    def get_branch_city(self, obj):
        branch = obj.branch
        if branch and branch.location:
            return branch.location.city
        return None

    def get_appointment_date(self, obj):
        return obj.appointment_date.strftime('%d-%m-%Y')

    def get_appointment_time(self, obj):
        return obj.appointment_time.strftime('%H:%M')

    def get_stylist_name(self, obj):
        """Fetch stylist name from Staff table instead of Beautician."""
        if obj.stylist_id:
            try:
                return Staff.objects.get(staff=obj.stylist_id).name
            except Staff.DoesNotExist:
                return None
        return None

    def get_stylist_id(self, obj):
        """Return stylist ID from Staff table."""
        return obj.stylist_id if obj.stylist_id else None

    def get_stylist_photo(self, obj):
        """Fetch stylist photo from Staff table."""
        if obj.stylist_id:
            try:
                staff = Staff.objects.get(staff=obj.stylist_id)
                return staff.photo.url if staff.photo else None
            except Staff.DoesNotExist:
                return None
        return None
    def get_reference_image(self, obj):
        """Fetch reference image from table."""
        
        if obj.reference_image:  # Check if reference_image is not None or empty
            return settings.MEDIA_URL + str(obj.reference_image)
        
        return ""  # Return empty value if reference_image is null/empty


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['message_id', 'text']

class FrequentlyUsedServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)

    class Meta:
        model = Services
        fields = ['service_id', 'service_name', 'image', 'price', 'category_name']

class CallbackRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackRequest
        fields = ['name', 'phone', 'user', 'status']
        extra_kwargs = {
            'name': {'required': True},  # Ensure name is required
        }

class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ['email']

class ReviewsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['review_id', 'rating', 'comment', 'user_name', 'created_at', 'status']

    def get_rating(self, obj):
        return f"{obj.rating:.1f}"



class ServicesProviderSerializer(serializers.ModelSerializer):
    reviews = ReviewsSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceProvider
        fields = ['provider_id', 'name', 'reviews']  # Remove review_count and average_rating



class BookingSerializer(serializers.ModelSerializer):
    branch_name = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    stylist_name = serializers.SerializerMethodField()
    status_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    payment_amount = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()
    reason = serializers.SerializerMethodField()
    # message = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'appointment_id', 'formatted_date', 'formatted_time', 'branch_name', 
            'services', 'stylist_name', 'status_name', 'username', 'payment_amount','reason'
        ]

    def get_formatted_date(self, obj):
        return obj.appointment_date.strftime('%d/%m/%Y')

    def get_formatted_time(self, obj):
        return obj.appointment_time.strftime('%H:%M')

    def get_branch_name(self, obj):
        if obj.branch:
            return obj.branch.branch_name
        return None

    def get_services(self, obj):
        service_ids = obj.service_id_new.split(',')
        services = Services.objects.filter(service_id__in=service_ids)
        return [service.service_name for service in services]

    def get_stylist_name(self, obj):
        if obj.stylist:
            return obj.stylist.name
        return None

    def get_status_name(self, obj):
        if obj.status:
            return obj.status.status_name
        return None

    def get_username(self, obj):
        return obj.user.name  # Assuming 'name' is the field in the 'User' model

    def get_payment_amount(self, obj):
      payment = Payment.objects.filter(appointment=obj).first()
      if payment:
          return payment.grand_total
      return None
    
    def get_reason(self, obj):
        if obj.reason is not None:
            return obj.reason

        # Fetch message text using message_id
        message_txt = Message.objects.filter(message_id=obj.message).first()

        return message_txt.text if message_txt else None



class UsersSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(
        input_formats=["%d-%m-%Y"], 
        format="%d-%m-%Y", 
        required=False, 
        allow_null=True
    )

    def to_internal_value(self, data):
        if 'dob' in data and data['dob'] in [None, '']:
            data['dob'] = None  # Convert empty string to None
        return super().to_internal_value(data)

    class Meta:
        model = User
        fields = ['user_id', 'name', 'email', 'phone', 'dob', 'gender', 'location', 'address']
        extra_kwargs = {
            'dob': {'required': False, 'allow_null': True},
            'gender': {'required': False},
            'location': {'required': False},
            'address': {'required': False},
        }


class ContactFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = ['name', 'email', 'message']