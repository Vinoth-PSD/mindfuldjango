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
    class Meta:
        model = ServiceProvider
        fields = '__all__'

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
        ]

    def get_service_names(self, obj):
        service_ids = obj.service_id_new.split(',')  # Assuming service_id_new is a comma-separated list of service IDs
        services = Services.objects.filter(service_id__in=service_ids)
        service_details = [
            {"service_name": service.service_name, "price": float(service.price) if service.price else 0}
            for service in services
        ]
        return service_details  # Return an array of dictionaries containing the service details


    def get_branch_city(self, obj):
        branch = obj.branch
        if branch and branch.location:
            return branch.location.city
        return None

    def get_appointment_date(self, obj):
        return obj.appointment_date.strftime('%d-%m-%Y')

    def get_appointment_time(self, obj):
        return obj.appointment_time.strftime('%H:%M')
