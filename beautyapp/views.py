from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from .models import ServiceProvider
from .serializers import ServiceProviderSerializer
from .models import ServiceProvider
from .models import Beautician
from .serializers import BeauticianSerializer
from rest_framework import viewsets
from django.db import connection
from django.db.models import Q
from django.conf import settings
from .models import Photo
from .serializers import PhotoSerializer
from .models import FAQ
from .serializers import FAQSerializer
from .serializers import UserSerializer
from .models import User
from .models import Staff
from .serializers import StaffSerializer

from .models import ServiceTypes
from .serializers import ServiceTypesSerializer

from .models import Serviceprovidertype


from .serializers import ServiceprovidertypeSerializer

from .models import Services
from .serializers import ServicesSerializer

from .models import StaffReview
from .serializers import StaffReviewSerializer

from .models import Appointment
from .serializers import AppointmentSerializer

from .models import Payment
from .serializers import PaymentSerializer

from .models import CustomerFeedback
from .serializers import CustomerFeedbackSerializer

from .models import Category
from .serializers import CategorySerializer

from .models import Subcategory
from .serializers import SubcategorySerializer

from rest_framework.decorators import action
from .models import Login
from .serializers import LoginSerializer
from django.utils import timezone
from datetime import timedelta

from .serializers import AvailableSlotsSerializer

from .models import Review , Branches
from .serializers import ReviewSerializer

import random
import string

from datetime import datetime

from .models import Coupon
from .serializers import CouponSerializer

from .models import ServiceFAQ
from .serializers import ServiceFAQSerializer,MessageSerializer,FrequentlyUsedServiceSerializer,CallbackRequestSerializer,NewsletterSerializer,ServicesProviderSerializer,BookingSerializer,UsersSerializer,ContactFormSerializer,ReviewsSerializer,BranchSerializer
from django.db import transaction
from decimal import Decimal
from django.db.models import Sum
from .models import Status,Message,CallbackRequest,Newsletter,Locations
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Avg, FloatField, Q
from django.db.models.functions import Round, Cast
from rest_framework.decorators import api_view
from django.db.models.functions import Length
from django.db.models import F, Func, Value, FloatField,ExpressionWrapper
from django.db.models.expressions import RawSQL
from django.db.models.functions import ACos, Cos, Radians, Sin
from django.core.mail import send_mail
from django.utils.html import format_html
from django.db.models import DecimalField, Sum


class LoginViewSet(viewsets.ModelViewSet):
    queryset = Login.objects.all()
    serializer_class = LoginSerializer

    # Override the create method for initiating login (generating OTP)
    def create(self, request, *args, **kwargs):
      phone = request.data.get('phone')  # Get phone number from request
  
      if not phone:
          return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
  
      # Check if the phone number exists in the User table
      if not User.objects.filter(phone=phone).exists():
          return Response({'status': 'failure', 'message': 'This mobile number is not registered. Please register first to log in.'}, status=status.HTTP_400_BAD_REQUEST)
  
      # Generate a random 6-digit OTP
      otp = ''.join(random.choices(string.digits, k=4))
  
      # Get or create the Login entry for the phone number
      login_entry, created = Login.objects.get_or_create(phone=phone)
      if created:
          # Set OTP and timestamp for new entries
          login_entry.otp = otp
          login_entry.otp_created_at = timezone.now()
          login_entry.save()
          message = 'OTP generated and sent successfully'
      else:
          # Update OTP and timestamp for existing entries
          login_entry.otp = otp
          login_entry.otp_created_at = timezone.now()
          login_entry.save()
          message = 'OTP updated successfully'
  
          # Send OTP via SMS using the MindfulBeautySendSMS class
          sms = MindfulBeautySendSMS()
          user_entry = User.objects.get(phone=phone)  # Get user details
          sms_response = sms.send_sms(name=user_entry.name, otp=otp, numbers=phone)

  
      # Log the SMS API response (optional)
      print(f"SMS API Response: {sms_response}")
  
      return Response({'status': 'success', 'otp': otp, 'message': message}, status=status.HTTP_200_OK)

    # Define a custom action for verifying OTP
    
    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request, *args, **kwargs):
        phone = request.data.get('phone')  # Get phone number from request
        otp = request.data.get('otp')  # Get OTP from request
        
        if not phone or not otp:
            return Response({'status': 'failure', 'message': 'Phone and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check if the phone number exists in the User table
            if not User.objects.filter(phone=phone).exists():
                return Response({'status': 'failure', 'message': 'User not registered'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Retrieve the User and Login entries
            user_entry = User.objects.get(phone=phone)
            login_entry = Login.objects.get(phone=phone)
        except Login.DoesNotExist:
            return Response({'status': 'failure', 'message': 'Invalid phone number'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate OTP
        if login_entry.otp == int(otp):
            # Generate a random token manually
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
            
            # Save the token to the login entry
            login_entry.token = token
            login_entry.save()
            
            # Return the token along with success message and user_id
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'token': login_entry.token,
                'user_id': user_entry.user_id
            }, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'failure', 'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer

class ServiceTypesViewSet(viewsets.ModelViewSet):
    queryset = ServiceTypes.objects.all().order_by('-service_type_id')  # Order by service_type_id in descending order
    serializer_class = ServiceTypesSerializer

class ServiceProviderSearchAPIView(APIView):

    def get_lat_lng(self, address):
        api_key = 'AIzaSyAJMgVfZLEI4QjXqVEQocAmgByXIKgwKwQ'
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'address': address, 'key': api_key}
        response = requests.get(url, params=params)
        result = response.json()
        
        if result['status'] == 'OK':
            location = result['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            raise ValueError("Geocoding API error: " + result.get('status'))

    def get_distance_matrix(self, origins, destinations):
        api_key = 'AIzaSyAJMgVfZLEI4QjXqVEQocAmgByXIKgwKwQ'
        url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
        params = {'origins': '|'.join(origins), 'destinations': '|'.join(destinations), 'key': api_key}
        response = requests.get(url, params=params)
        result = response.json()

        # Debugging: Print the raw API response to understand its structure
        print("Distance Matrix API Response:", result)
        
        if result['status'] == 'OK':
            return result['rows']
        else:
            raise ValueError("Distance Matrix API error: " + result.get('status'))
        
def post(self, request):
        service_type = request.query_params.get('service_type')
        address = request.query_params.get('address')
        radius = request.query_params.get('radius')
        
        if not service_type or not address:
            return Response({"error": "Missing 'service_type' or 'address' parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Convert radius to float and handle invalid cases
            radius = float(radius) if radius is not None else 10  # Default to 10 km if radius is not provided
            
            # Get latitude and longitude for the address
            lat, lng = self.get_lat_lng(address)
            
            # Get all service providers
            providers = ServiceProvider.objects.filter(service_type=service_type)
            
            if not providers:
                return Response({"error": "No service providers found matching the service type"}, status=status.HTTP_404_NOT_FOUND)
            
            # Prepare origins and destinations
            provider_addresses = [
                f'{provider.address.address_line1}, {provider.address.city}, {provider.address.state} {provider.address.postal_code}'
                for provider in providers]
            origins = [f'{lat},{lng}']
            
            # Debugging: Print the origins and destinations
            print("Origins:", origins)
            print("Destinations:", provider_addresses)
            
            # Get distances from the address to each provider
            distances = self.get_distance_matrix(origins, provider_addresses)
            
            # Debugging: Print the distances to understand the structure
            print("Distances:", distances)
            
            # Filter based on distance
            nearby_providers = []
            for provider, distance in zip(providers, distances[0]['elements']):
                if 'distance' in distance and distance['status'] == 'OK':
                    distance_km = distance['distance']['value'] / 1000  # Convert meters to kilometers
                    if distance_km <= radius:
                        nearby_providers.append(provider)
                else:
                    print("Distance key missing or status not OK in response element:", distance)
            
            if not nearby_providers:
                return Response({"error": "No nearby service providers found within the radius"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = ServiceProviderSerializer(nearby_providers, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        

class BeauticianViewSet(viewsets.ModelViewSet):
    queryset = Beautician.objects.all()
    serializer_class = BeauticianSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": "success",
                    "message": "Beauticians retrieved successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": "failure",
                    "message": "Failed to retrieve beauticians",
                    "error": str(e),
                    "data": []
                },
                status=status.HTTP_404_NOT_FOUND)



class FilterAPIView(APIView):
    def get_lat_lng(self, address):
        api_key = 'AIzaSyAJMgVfZLEI4QjXqVEQocAmgByXIKgwKwQ'  # Replace with your actual API key
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'address': address, 'key': api_key}
        response = requests.get(url, params=params)
        result = response.json()
        
        if result['status'] == 'OK':
            location = result['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            raise ValueError("Geocoding API error: " + result.get('status'))
        
    def get_distance_matrix(self, origins, destinations):
        api_key = 'AIzaSyAJMgVfZLEI4QjXqVEQocAmgByXIKgwKwQ'  # Replace with your actual API key
        url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
        params = {'origins': '|'.join(origins), 'destinations': '|'.join(destinations), 'key': api_key}
        response = requests.get(url, params=params)
        result = response.json()
        
        if result['status'] == 'OK':
            return result['rows']
        else:
            raise ValueError("Distance Matrix API error: " + result.get('status'))
        
    def post(self, request, *args, **kwargs):
        service_type = request.query_params.get('service_type')
        address = request.query_params.get('address')
        radius = request.query_params.get('radius')
        service_id = request.query_params.get('service_id')

        if not service_type or not address:
            return Response({
                "status": "failure",
                "message": "Missing 'service_type', 'address', or 'radius' parameter.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            radius = float(radius) if radius is not None else 10
            
            lat, lng = self.get_lat_lng(address)
            
            providers = ServiceProvider.objects.filter(service_type=service_type)
            
            if service_id:
                providers = providers.filter(serviceprovidertype__service_id=service_id)

            if not providers.exists():
                return Response({
                    "status": "failure",
                    "message": "No service providers found matching the service type.",
                    "data": []
                }, status=status.HTTP_404_NOT_FOUND)
            
            provider_addresses = [
                f'{provider.address.address_line1}, {provider.address.city}, {provider.address.state} {provider.address.postal_code}'
                for provider in providers]
            origins = [f'{lat},{lng}']
            
            distances = self.get_distance_matrix(origins, provider_addresses)
            
            base_url = 'http://127.0.0.1:8000'
            
            nearby_providers = []
            for provider, distance in zip(providers, distances[0]['elements']):
                if 'distance' in distance and distance['status'] == 'OK':
                    distance_km = distance['distance']['value'] / 1000
                    if distance_km <= float(radius):
                        image_url = None
                        if provider.image_url:
                            # image_url = base_url + settings.MEDIA_URL + str(provider.image_url)
                            image_url = settings.MEDIA_URL + str(provider.image_url)
                        
                        # Retrieve all services offered by the provider
                        all_services = Serviceprovidertype.objects.filter(provider_id=provider).select_related('service_id')
                    
                        # Generate a comma-separated string of service names
                        services_list = ', '.join([service.service_id.service_name for service in all_services])

                        nearby_providers.append({
                            "provider_name": provider.name,
                            "rating": provider.rating,
                            "review_count": "69.2K reviews",  # Replace with actual data
                            "service_type": provider.service_type.type_name,  # Replace with actual data
                            "provider_city": f"{provider.address.city}",
                            "provider_state": f"{provider.address.state}",
                            "distance_km": f"{distance_km} km",
                            "image_url": image_url,
                            "verified": True,  # Replace with actual verification status
                            "all_services": services_list , # Include the services provided by the provider
                            "service_type":f"{provider.service_type_id}",
                            "otp":"1234",
                        })

            if nearby_providers:
                return Response({
                    "status": "success",
                    "message": "Service providers retrieved successfully.",
                    "data": nearby_providers
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "failure",
                    "message": "No nearby service providers found within the radius.",
                    "data": []
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e),
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": "success",
                    "message": "Photos retrieved successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": "failure",
                    "message": "Failed to retrieve photos",
                    "error": str(e),
                    "data": []
                },
                status=status.HTTP_404_NOT_FOUND)

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'message': 'FAQs retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'failure',
                'message': 'Failed to retrieve FAQs',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):  
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'message': 'Users retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'status': 'failure',
                'message': 'Failed to retrieve users',
                'error': str(e)
            }, status=status.HTTP_200_OK)
    
    # POST method (create)
    def create(self, request, *args, **kwargs):  
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()  # Save the new user
                
                # Email subject
                email_subject = "Welcome to Mindful Beauty"

                # HTML Email Content with Logo
                email_message = format_html(
                    """
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <div style="text-align: center;">
                            <img src="https://mbimagestorage.blob.core.windows.net/mbimages/mindfulBeautyLogoSmall-CXWufzBM.png" alt="Mindful Beauty" style="width: 150px; margin-bottom: 20px;">
                        </div>
                        <h2 style="color: #333;">Welcome, {name}!</h2>
                        <p style="font-size: 16px; color: #555;">
                            We are delighted to have you on board. Your registration has been successfully completed.
                            You can now access your account and explore our services.
                        </p>
                        <hr style="margin: 20px 0;">
                        <p style="font-size: 14px; text-align: center; color: #777;">
                            Best Regards,<br>
                            <strong>Mindful Beauty Team</strong>
                        </p>
                    </div>
                    """,
                    name=user.name  # Dynamically insert user's name
                )

                # Try to send the email
                try:
                    send_mail(
                        email_subject,
                        '',  # Plain text version (empty since we're sending HTML)
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],  # Send to registered user
                        fail_silently=True,  # Fail silently to prevent errors
                        html_message=email_message  # HTML email content
                    )
                    email_status = "Email sent successfully"
                except Exception as e:
                    email_status = f"Email failed: {str(e)}"  # Log the error but continue

                return Response({
                    'status': 'success',
                    'message': 'User created successfully',
                    'email_status': email_status,  # Show email status in response
                    'data': serializer.data
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    'status': 'failure',
                    'message': 'User creation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'failure',
                'message': 'An error occurred while creating the user',
                'error': str(e)
            }, status=status.HTTP_200_OK)  # Changed 404 to 200 to avoid breaking flow


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": "success",
                    "message": "Staff list retrieved successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": "failure",
                    "message": "Failed to retrieve staff list",
                    "error": str(e),
                    "data": []
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        phone = request.data.get("phone")
        if phone:
            # Check if the phone number already exists
            if Staff.objects.filter(phone=phone).exists():
                return Response(
                    {
                        "status": "failure",
                        "message": "A staff member with this phone number already exists."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Proceed with the normal creation process if phone number is unique
        return super().create(request, *args, **kwargs)
    

class ServiceprovidertypeViewSet(viewsets.ModelViewSet):
    queryset = Serviceprovidertype.objects.all()
    serializer_class = ServiceprovidertypeSerializer

    # Geocoding function to get latitude and longitude based on address
    def get_lat_lng(self, address):
        api_key = 'AIzaSyAJMgVfZLEI4QjXqVEQocAmgByXIKgwKwQ'  # Replace with your actual API key
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'address': address, 'key': api_key}
        response = requests.get(url, params=params)
        result = response.json()

        if result['status'] == 'OK':
            location = result['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            raise ValueError("Geocoding API error: " + result.get('status'))

    # Function to calculate distances using Google Distance Matrix API
    def get_distance_matrix(self, origins, destinations):
        api_key = 'AIzaSyAJMgVfZLEI4QjXqVEQocAmgByXIKgwKwQ'  # Replace with your actual API key
        url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
        params = {'origins': '|'.join(origins), 'destinations': '|'.join(destinations), 'key': api_key}
        response = requests.get(url, params=params)
        result = response.json()

        if result['status'] == 'OK':
            return result['rows']
        else:
            raise ValueError("Distance Matrix API error: " + result.get('status'))
    


    def list(self, request, *args, **kwargs):
        service_id = request.query_params.get('service_id')
        category_id = request.query_params.get('category_id')
        address = request.query_params.get('address')
        radius = request.query_params.get('radius')
        service_type_id = request.query_params.get('service_type_id')
        open_now = request.query_params.get('open_now')  #0 is close 1 is opened

        #if not service_id or not address or not radius or not category_id:
        if not (service_id or category_id) or not address or not radius:
            return Response(
                {
                    "status": "failure",
                    "message": "Missing required query parameters: service_id, category_id , address, or radius",
                    "data": []
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            

        try:
            # Get latitude and longitude from the provided address (Assuming you have a method for this)
            lat, lng = self.get_lat_lng(address)

            # Use the model class to call the method
            results = Serviceprovidertype().get_provider_services_with_cursor(
                service_id, lat, lng, radius, service_type_id , category_id
            )

            if results:
                return Response(
            {
                "status": "success",
                "message": "Filtered service provider retrieved successfully",
                "data": results
            },
            status=status.HTTP_200_OK
        )
            else:
                return Response(
            {
                "status": "failure",
                "message": "No service providers found",
                "data": []
            },
            status=status.HTTP_200_OK
        )
            
        except Exception as e:
            return Response(
                {
                    "status": "failure",
                    "message": "Failed to retrieve service provider",
                    "error": str(e),
                    "data": []
                },
                status=status.HTTP_404_NOT_FOUND
            )

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 200  # Default number of records per page
    page_size_query_param = 'page_size'  # Optional, to allow clients to set the page size
    max_page_size = 500  # Optional, to limit the maximum number of records per page


class ServicesViewSet(viewsets.ModelViewSet):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer
    #pagination_class = None
    pagination_class = StandardResultsSetPagination
    
    
class StaffReviewViewSet(viewsets.ModelViewSet):
    queryset = StaffReview.objects.all()
    serializer_class = StaffReviewSerializer

    def list(self, request, *args, **kwargs):
        """Handles GET request for retrieving all staff reviews."""
        queryset = self.filter_queryset(self.get_queryset())
        
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": "success",
                "message": "Staff reviews retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failure",
                "message": "No staff reviews found.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)
        

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def list(self, request, *args, **kwargs):
        """Handles GET request for retrieving all appointments."""
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": "success",
                "message": "Appointments retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failure",
                "message": "No appointments found.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

    

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'message': 'Payments retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'failure',
                'message': 'Failed to retrieve payments',
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)


class CustomerFeedbackViewSet(viewsets.ModelViewSet):
    queryset = CustomerFeedback.objects.all()
    serializer_class = CustomerFeedbackSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "status": "success",
                    "message": "Feedbacks retrieved successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": "failure",
                    "message": "Failed to retrieve feedbacks",
                    "error": str(e),
                    "data": []
                },
                status=status.HTTP_404_NOT_FOUND)

    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()  # Required for DRF router
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": "success",
                "message": "Categories retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failure",
                "message": "No categories found",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)


class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()  # Required for DRF router
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        queryset = Subcategory.objects.filter(is_deleted=False)
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": "success",
                "message": "Subcategories retrieved successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failure",
                "message": "No subcategories found",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)



class BookServiceViewSet(viewsets.ModelViewSet):
    queryset = Serviceprovidertype.objects.all()
    serializer_class = ServiceprovidertypeSerializer

    def list(self, request, *args, **kwargs):
        branch_id = request.query_params.get('branch_id')
        provider_id = request.query_params.get('provider_id')
        service_id = request.query_params.get('service_id')
        category_id = request.query_params.get('category_id')
        subcategory_id = request.query_params.get('subcategory_id')

        if not provider_id and branch_id:
            return Response(
                {
                    "status": "failure",
                    "message": "Missing required query parameters: provider_id or branch_id missing ",
                    "data": []
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Initialize the Serviceprovidertype object
            service_provider_type = Serviceprovidertype()

            # Fetching the details based on provider_id
            provider_details = service_provider_type.get_provider_details(provider_id , branch_id)
            provider_services = service_provider_type.get_provider_services(provider_id, branch_id ,service_id, category_id, subcategory_id)
            beauticians = service_provider_type.get_beauticians_for_provider(provider_id,branch_id)
            provider_photos = service_provider_type.get_provider_photos(provider_id, 0)
            provider_banner = service_provider_type.get_provider_photos(provider_id, 1)
            faq = service_provider_type.get_faqs_for_provider(provider_id)
            overview = service_provider_type.get_overview_for_provider(provider_id)
            review = service_provider_type.get_reviews_by_provider(provider_id)
            packages = service_provider_type.get_provider_packages(provider_id ,branch_id)

            # Fetching frequently used services
            frequently_used_services = service_provider_type.get_frequently_used_services(provider_id , branch_id)    

            return Response(
                {
                    "status": "success",
                    "message": "Filtered service provider types retrieved successfully",
                    "data": provider_details,
                    "services": provider_services,
                    "stylist": beauticians,
                    "photos": provider_photos,
                    "banner": provider_banner,
                    "faq": faq,
                    "overview": overview,
                    "packages": packages,
                    "frequently_used_services": frequently_used_services.get("data", []),
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": "failure",
                    "message": "Failed to retrieve service provider types",
                    "error": str(e),
                    "data": []
                },
                status=status.HTTP_404_NOT_FOUND
            )



class AvailableSlotsViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = AvailableSlotsSerializer

    # Override list method to filter only available slots and optionally filter by provider_id
    def list(self, request, *args, **kwargs):
        # Check if provider_id is provided in the request body
        provider_id = request.query_params.get('provider_id')

        if provider_id:
            # Filter by the specific provider_id
            try:
                service_providers = ServiceProvider.objects.filter(provider_id=provider_id, available_slots__isnull=False)
            except ServiceProvider.DoesNotExist:
                return Response({'error': 'Service provider not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Return all service providers with available slots if no provider_id is specified
            service_providers = ServiceProvider.objects.filter(available_slots__isnull=False)

        # Serialize the filtered service providers
        serializer = self.get_serializer(service_providers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Override the retrieve method to return available slots for a specific provider
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # Handle updating available slots based on current time
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Get the current time (you can modify the format if needed)
        current_time = datetime.now().strftime("%I:%M %p")  # Current time in 12-hour format (e.g., 12:30 PM)

        # Process the available slots to turn off past times
        updated_slots = []
        slots_list = instance.available_slots[0].split(',')  # Assuming the available slots are a single string

        for slot_time in slots_list:
            slot_time = slot_time.strip()  # Remove any leading/trailing spaces
            # Check if the slot time is in the future or current
            if self.is_past_time(slot_time, current_time):
                updated_slots.append({'time': slot_time, 'status': 'off'})
            else:
                updated_slots.append({'time': slot_time, 'status': 'on'})

        # Update the service provider's available slots
        instance.available_slots = updated_slots
        instance.save()

        # Return success response
        return Response({
            'status': 'success',
            'message': 'Available slots updated successfully based on current time.',
            'data': instance.available_slots
        }, status=status.HTTP_200_OK)

    def is_past_time(self, slot_time, current_time):
        """
        Helper method to check if a time slot is in the past based on current time.
        """
        try:
            # Convert both slot_time and current_time to datetime objects
            slot_time_obj = datetime.strptime(slot_time, "%I:%M %p")
            current_time_obj = datetime.strptime(current_time, "%I:%M %p")
            return slot_time_obj < current_time_obj
        except ValueError:
            return False


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def create(self, request, *args, **kwargs):
        provider_id = request.data.get('provider')
        user_id = request.data.get('user_id')

        # Check if the review already exists for the user and provider
        existing_review = Review.objects.filter(provider_id=provider_id, user_id=user_id).first()

        if existing_review:
            # Update the existing review's comment and rating
            existing_review.comment = request.data.get('comment')
            existing_review.rating = request.data.get('rating', existing_review.rating)  # Optional update for rating
            existing_review.save()
            return Response({
                'status': 'success',
                'message': 'Review updated successfully.',
                'data': self.get_serializer(existing_review).data
            }, status=status.HTTP_200_OK)

        # Create a new review if it doesn't exist
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'failure',
                'message': 'Validation failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        review = serializer.save()

        return Response({
            'status': 'success',
            'message': 'Review created successfully.',
            'data': self.get_serializer(review).data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Check if the instance exists
        if not instance:
            return Response({
                'status': 'failure',
                'message': 'Review not found.',
            }, status=status.HTTP_200_OK)

        # Update the review fields
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response({
                'status': 'failure',
                'message': 'Validation failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)

        return Response({
            'status': 'success',
            'message': 'Review updated successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
class CouponAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        # Get the required fields from the request
        coupon_code = request.data.get('coupon_code')
        provider_id = request.data.get('provider')  # Assuming you pass the provider ID

        # Initialize response data
        response_data = {'data': {}}

        # Validate if coupon code and provider are provided
        if not coupon_code:
            response_data['status'] = 'failure'
            response_data['message'] = 'coupon_code is required'
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        if not provider_id:
            response_data['status'] = 'failure'
            response_data['message'] = 'provider is required'
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Create the coupon instance with automatic values
        try:
            coupon = Coupon.objects.create(
                provider_id=provider_id,
                coupon_code=coupon_code,
                coupon_limit=request.data.get('coupon_limit', 0),  # Default to 0 if not provided
                valid_from=datetime.now(),  # Set current date/time as valid_from
                valid_until=datetime.now() + timedelta(days=30),  # Set valid_until to 30 days from now
                discount_type=request.data.get('discount_type', 'percentage'),  # Default to 'percentage'
                discount_value=request.data.get('discount_value', 0.00),  # Default to 0.00
                status=request.data.get('status', 1),  # Default to 1 if not provided
            )
            response_data['status'] = 'success'
            response_data['message'] = 'Coupon created successfully'
            response_data['data'] = CouponSerializer(coupon).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            response_data['status'] = 'failure'
            response_data['message'] = str(e)  # Capture the error message
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyCouponAPIView(APIView):

    def post(self, request, *args, **kwargs):
        # Get the coupon code from the request
        coupon_code = request.data.get('coupon_code')

        # Initialize response data
        response_data = {'data': {}}

        # Validate if coupon code is provided
        if not coupon_code:
            response_data['status'] = 'failure'
            response_data['message'] = 'coupon_code is required'
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Check if the coupon exists and is valid
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code)
            current_time = datetime.now()

            # Check if the coupon is valid (within the valid_from and valid_until dates)
            valid_from = coupon.valid_from
            valid_until = coupon.valid_until

            # Ensure valid_from and valid_until are not None before comparison
            if valid_from and valid_until:
                if valid_from <= current_time <= valid_until:
                    response_data['status'] = 'success'
                    response_data['message'] = 'Coupon is valid'
                    response_data['data'] = CouponSerializer(coupon).data
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    response_data['status'] = 'failure'
                    response_data['message'] = 'Coupon is expired or not yet valid'
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                response_data['status'] = 'failure'
                response_data['message'] = 'Coupon has invalid date range'
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Coupon.DoesNotExist:
            response_data['status'] = 'failure'
            response_data['message'] = 'Coupon not found'
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            response_data['status'] = 'failure'
            response_data['message'] = str(e)  # Capture the error message
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
        
class ServiceFAQViewSet(viewsets.ModelViewSet):
    queryset = ServiceFAQ.objects.all()
    serializer_class = ServiceFAQSerializer

    def list(self, request, *args, **kwargs):
        service_type = request.query_params.get('service_type', None)

        # Check if service_type is provided
        if service_type is None:
            return Response(
                {
                    "message": "failure",
                    "detail": "service_type is a required field."
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service_type = int(service_type)
        except ValueError:
            return Response(
                {
                    "message": "failure",
                    "detail": "service_type must be an integer."
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filter data based on service_type
        queryset = ServiceFAQ.objects.filter(service_type=service_type)

        if not queryset.exists():
            return Response(
                {
                    "message": "failure",
                    "detail": "No FAQs found for the given service_type."
                }, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the filtered data
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                "message": "success",
                "data": serializer.data
            }, 
            status=status.HTTP_200_OK
        )

class AddToCartAPIView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        provider_id = request.data.get('provider_id')
        service_ids = request.data.get('service_ids')
        appointment_date = request.data.get('appointment_date')
        appointment_time = request.data.get('appointment_time')
        branch_id = request.data.get('branch_id')
        quantity = request.data.get('quantity')

        # Ensure all required fields are provided
        if not all([user_id, provider_id, service_ids, appointment_date, appointment_time, quantity]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Parse appointment_date
            appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()

            # Validate and convert appointment_time to 24-hour format
            try:
                # Convert to 24-hour time format (e.g., '11:30 AM' -> '11:30:00')
                parsed_time = datetime.strptime(appointment_time, "%I:%M %p")  # 12-hour format with AM/PM
                appointment_time_24hr = parsed_time.time()  # Get the time part only
            except ValueError:
                return Response({"error": "Invalid time format. Use 'HH:MM AM/PM'."}, status=status.HTTP_400_BAD_REQUEST)

            # Proceed with existing logic for services and quantity
            service_ids_list = [int(service_id.strip()) for service_id in service_ids.split(",")]
            quantity_list = [int(q.strip()) for q in quantity.split(",")]

            if len(service_ids_list) != len(quantity_list):
                return Response({"error": "Service IDs and quantity values must have the same length."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the Status object with status_id=0 (assuming '0' represents the default status)
            status_obj = Status.objects.get(status_id=0)
            service_ids_string = ",".join(map(str, service_ids_list))
            quantity_string = ",".join(map(str, quantity_list))

            # # Check if an appointment already exists with the same user, provider, branch, date, and time
            # existing_appointment = Appointment.objects.filter(
            #     user_id=user_id,
            #     provider_id=provider_id,
            #     branch_id=branch_id,
            #     appointment_date=appointment_date,
            #     appointment_time=appointment_time_24hr,
            #     status=status_obj
            # ).exists()

            # if existing_appointment:
            #     return Response({"error": "You already have an appointment at this time."}, status=status.HTTP_200_OK)

            # Use a transaction to ensure atomicity of the operation
            with transaction.atomic():
                # Create the Appointment object
                appointment = Appointment.objects.create(
                    user_id=user_id,
                    provider_id=provider_id,
                    service_id_new=service_ids_string,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time_24hr,  # Save in 24-hour format
                    status=status_obj,
                    branch_id=branch_id,
                    quantity=quantity_string
                )

            # Return the appointment ID in the response
            return Response({
                "status": "success",
                "message": "Appointments added to cart successfully.",
                "appointment_id": appointment.appointment_id  # Include the appointment_id in the response
            }, status=status.HTTP_201_CREATED)

        except Status.DoesNotExist:
            return Response({"error": "Default status not found."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Booking List       
class BookingListAPIView(APIView):
    def get(self, request):
        provider_id = request.query_params.get("provider_id")
        sort_order = request.query_params.get("sort_order", "desc")

        if not provider_id:
            return Response(
                {"status": "error", "message": "Provider ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            provider_id = int(provider_id)
            now = datetime.now()
            order_by_field = "-appointment_id" if sort_order == "desc" else "appointment_id"

            bookings = (
                Appointment.objects.filter(
                    provider_id=provider_id,
                    status_id=0,
                    appointment_date__gte=now.date(),
                )
                .exclude(branch__isnull=True)  # Ensure branch exists
                .select_related("branch")  # Optimize DB queries
                .order_by(order_by_field)
            )

            serializer = AppointmentSerializer(bookings, many=True)
            return Response(
                {
                    "status": "success",
                    "message": "Fetched successfully",
                    "bookings": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError:
            return Response(
                {"status": "error", "message": "Invalid provider ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

#Provider booking action
class ProviderActionAPIView(APIView):
    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        action_id = request.data.get('action_id')
        stylist_id = request.data.get('stylist_id') 
        freelancer = request.data.get('freelancer', False) 

        if not appointment_id or action_id is None:
            return Response(
                {"status": "error", "message": "Appointment ID and action_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            action_mapping = {
                1: "accept",
                2: "decline"
            }

            action = action_mapping.get(action_id)
            if not action:
                return Response(
                    {"status": "error", "message": "Invalid action_id provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            appointment = Appointment.objects.get(appointment_id=appointment_id)

            if appointment.status_id == 4:
                return Response(
                    {"status": "error", "message": "This appointment has been canceled and cannot be accepted."},
                    status=status.HTTP_403_FORBIDDEN
                )

            provider = ServiceProvider.objects.get(provider_id=appointment.provider_id)

            if provider.available_credits < 1000:
                return Response(
                    {"status": "failure", "message": "The minimum wallet amount should be 1000. Please add the amount to the wallet."},
                    status=status.HTTP_403_FORBIDDEN
                )

            service_ids = appointment.service_id_new.split(",")  
            total_price = Services.objects.filter(service_id__in=service_ids, is_deleted=False).aggregate(
                total=Sum(Cast("price", output_field=DecimalField()))
            )["total"] or 0  

            required_credits = total_price * 0.3

            if provider.available_credits < required_credits:
                return Response(
                    {
                        "status": "failure",
                        "message": f"Insufficient wallet balance"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            if action == "accept":
                appointment.status_id = 1  
                
                otp = "1234"  
                appointment.otp = otp
                
                if not freelancer and stylist_id:
                    appointment.stylist_id = stylist_id

                appointment.save()

                user = User.objects.get(user_id=appointment.user_id)
                user_phone = user.phone

                # Send OTP via SMS
                sms_service = MindfulBeautySendSMS()
                sms_response = sms_service.send_sms(name=user.name, otp=otp, numbers=user_phone)

                return Response(
                    {
                        "status": "success",
                        "message": "Appointment accepted and scheduled",
                        "otp": otp,
                        "stylist_id": stylist_id or "No stylist assigned",
                        "sms_response": sms_response
                    },
                    status=status.HTTP_200_OK
                )

            elif action == "decline":
                appointment.status_id = 4  # Canceled
                appointment.otp = None  
                appointment.save()

                return Response(
                    {
                        "status": "success",
                        "message": f"Appointment {action}d successfully"
                    },
                    status=status.HTTP_200_OK
                )

        except Appointment.DoesNotExist:
            return Response(
                {"status": "error", "message": "Appointment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except User.DoesNotExist:
            return Response(
                {"status": "error", "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except ServiceProvider.DoesNotExist:
            return Response(
                {"status": "error", "message": "Service provider not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#Deny Appointment 
class DeclineAppointmentMessageAPIView(APIView):
    def post(self, request):
        # Get the appointment ID and message ID from the request
        appointment_id = request.data.get('appointment_id')
        message_id = request.data.get('message_id')

        # Validate appointment_id and message_id
        if not appointment_id or not message_id:
            return Response(
                {"status": "error", "message": "Appointment ID and message ID are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch the appointment and message
            appointment = Appointment.objects.get(appointment_id=appointment_id)
            message = Message.objects.get(message_id=message_id)

            user = appointment.user  

            # Store the message_id in the appointment
            appointment.message = str(message.message_id)  # Store message_id as string
            appointment.status_id = 4  # Set status to 'cancelled'
            appointment.save()

            email_status = "No email sent"  # Default email status

            # Send cancellation email to the user
            subject = "Your Appointment Has Been Cancelled"

            # HTML Email Template
            email_body = format_html(
                """
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <div style="text-align: center;">
                        <img src="https://mbimagestorage.blob.core.windows.net/mbimages/mindfulBeautyLogoSmall-CXWufzBM.png" alt="Mindful Beauty" style="width: 150px; margin-bottom: 20px;">
                    </div>
                    <h2 style="color: #d9534f;">Dear {name},</h2>
                    <p style="font-size: 16px; color: #555;">
                        We regret to inform you that your appointment (ID: <strong>{appointment_id}</strong>) has been cancelled.
                    </p>
                    <p style="font-size: 16px; color: #555;">
                        <strong>Reason for cancellation:</strong><br>
                        "{reason}"
                    </p>
                    <p style="font-size: 16px; color: #777;">
                        If you have any questions, please contact us.
                    </p>
                    <hr style="margin: 20px 0;">
                    <p style="font-size: 14px; text-align: center; color: #777;">
                        Best Regards,<br>
                        <strong>Mindful Beauty Team</strong>
                    </p>
                </div>
                """,
                name=user.name,
                appointment_id=appointment_id,
                reason=message.text
            )

            # Try to send the email
            try:
                send_mail(
                    subject,
                    '',  # Empty plain text (since we send HTML)
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],  # Sending to user's email
                    fail_silently=True,  # Fail silently to prevent API crash
                    html_message=email_body  # HTML email content
                )
                email_status = "Email sent successfully"
            except Exception as e:
                email_status = f"Email failed: {str(e)}"

            # Return a success response
            return Response(
                {
                    "status": "success",
                    "message": "Appointment canceled by provider and email sent to the user",
                    "email_status": email_status,  # Email status added
                },
                status=status.HTTP_200_OK
            )

        except Appointment.DoesNotExist:
            return Response(
                {"status": "error", "message": "Appointment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Message.DoesNotExist:
            return Response(
                {"status": "error", "message": "Message not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#Appointment status
class AppointmentStatusAPIView(APIView):
    def get(self, request):
        appointment_id = request.query_params.get('appointment_id')  # Get appointment_id from query parameters
        
        if not appointment_id or appointment_id == '0':
            return Response(
                {"status": "error", "message": "Appointment ID is required"},
                status=status.HTTP_200_OK
            )
        try:
            # Fetch the appointment using the appointment_id
            appointment = Appointment.objects.get(appointment_id=appointment_id)

            # Return the status_id of the appointment
            return Response(
                {"status": "success", "appointment_id": appointment_id, "status_id": appointment.status_id},
                status=status.HTTP_200_OK
            )

        except Appointment.DoesNotExist:
            return Response(
                {"status": "error", "message": "Appointment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        
#OTP Verification        
class OTPVerificationAPIView(APIView):
    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        otp = request.data.get('otp')  

        if not all([appointment_id, otp]):
            return Response(
                {"status": "error", "message": "Both appointment_id and otp are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            appointment = Appointment.objects.get(appointment_id=appointment_id, otp=otp)

            if appointment.otp == otp:
                return Response(
                    {"status": "success", "message": "OTP verified successfully."}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"status": "error", "message": "Invalid OTP."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Appointment.DoesNotExist:
            return Response(
                {"status": "error", "message": "Appointment not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AddPaymentAPIView(APIView):
    def post(self, request):
        """
        Handles storing payment data based on appointment_id, coupon code, and amount.
        Calculates SGST, CGST, and Grand Total from the amount and stores them.
        """
        appointment_id = request.data.get("appointment_id")
        coupon_code = request.data.get("coupon_code", "")
        coupon_amount = request.data.get("coupon_amount", 0)
        amount = request.data.get("amount")  

        if not appointment_id or not amount:
            return Response({"error": "Appointment ID and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                appointment = Appointment.objects.get(appointment_id=appointment_id)

                # Ensure amount and coupon_amount are decimals
                coupon_amount = Decimal(coupon_amount)
                amount = Decimal(amount)

                # Calculate CGST, SGST, and Grand Total
                cgst = (amount * Decimal(9)) / Decimal(100)  # 9% CGST
                sgst = (amount * Decimal(9)) / Decimal(100)  # 9% SGST
                grand_total = amount + cgst + sgst - coupon_amount

                # Create payment record
                payment = Payment.objects.create(
                    appointment=appointment,
                    amount=amount,
                    coupon_code=coupon_code,
                    coupon_amount=coupon_amount,
                    payment_status="Pending",
                    cgst=int(cgst),
                    sgst=int(sgst),
                    grand_total=int(grand_total),
                )
                return Response({
                    "status": "success",
                    "message": "Payment recorded successfully",
                    "payment_id": payment.payment_id,
                    "amount": float(amount),
                    "coupon_code": coupon_code,
                    "coupon_amount": float(coupon_amount),
                    "cgst": int(cgst),
                    "sgst": int(sgst),
                    "grand_total": int(grand_total),
                }, status=status.HTTP_201_CREATED)

        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Messages
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    pagination_class = None  

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            "status": "success", 
            "message": "Messages retrieved successfully",  
            "data": serializer.data  
        })

#Frequently Used Services 
class FrequentlyUsedServicesAPIView(APIView):
    def get(self, request):
        # Extract and count the frequency of services based on appointments
        appointments = Appointment.objects.values_list('service_id_new', flat=True)
        service_count = {}

        # Split comma-separated service IDs and count their occurrences
        for service_ids in appointments:
            if service_ids:
                for service_id in service_ids.split(','):
                    service_id = service_id.strip()
                    if service_id.isdigit():  # Ensure valid service IDs
                        service_count[service_id] = service_count.get(service_id, 0) + 1

        # Get the top 3 most frequently used service IDs
        top_service_ids = sorted(service_count, key=service_count.get, reverse=True)[:3]

        if not top_service_ids:
            return Response({
                "status": "success",
                "message": "No frequently used services.",
                "data": []
            })

        # Fetch service details along with the category name
        services = Services.objects.filter(service_id__in=top_service_ids).select_related('category')

        # Serialize the data
        serializer = FrequentlyUsedServiceSerializer(services, many=True)
        return Response({
            "status": "success",
            "message": "Frequently used services fetched successfully.",
            "data": serializer.data
        })

#Call Back Request
class CallbackRequestCreateOrUpdateAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        # Extract the data from the request
        name = request.data.get('name')
        phone = request.data.get('phone')
        user_id = request.data.get('user')  # Optional

        # Check if name and phone are provided
        if not name or not phone:
            return Response({"error": "Both 'name' and 'phone' are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to find an existing CallbackRequest with the same phone number
        callback_request, created = CallbackRequest.objects.update_or_create(
            phone=phone,
            defaults={'name': name, 'user_id': user_id, 'status': 1}
        )
        
        # Serialize the data and return the response
        serializer = CallbackRequestSerializer(callback_request)
        if created:
            return Response({"message": "Callback request created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Callback request updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

#Newsletter 
class NewsletterSubscriptionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email already exists in the database
        if Newsletter.objects.filter(email=email).exists():
            return Response({"message": "You are already subscribed."}, status=status.HTTP_200_OK)
        
        # Otherwise, create a new subscription
        newsletter = Newsletter.objects.create(email=email)
        serializer = NewsletterSerializer(newsletter)
        return Response({"message": "Subscribed successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)


#Get city name
class CityViewSet(viewsets.ViewSet):
    def list(self, request):
        cities = Locations.objects.annotate(city_length=Length('city')).filter(city_length__gt=4).values_list('city', flat=True).distinct()
        return Response({"cities": cities})
    

#Get review with counting and rating
class ProvidersReviewViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        try:
            provider = ServiceProvider.objects.get(pk=pk)

            active_reviews = provider.reviews.filter(status=1)

            # Serialize the data
            provider_data = ServicesProviderSerializer(provider)
            reviews_data = ReviewsSerializer(active_reviews, many=True)

            return Response({
                "status": "success",  # Add status
                "message": "Reviews retrieved successfully",  # Add message
                **provider_data.data,  
                'reviews': reviews_data.data,  
            })

        except ServiceProvider.DoesNotExist:
            return Response({
                "status": "error",  # Add error status
                "message": "Service provider not found",  # Add error message
            }, status=404)

#My bookings 
class UserBookingsAPIView(APIView):
    
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if user_id:
            # Filter appointments for the user where otp is not null and not zero
            # Order the results by 'created_at' field in descending order
            bookings = Appointment.objects.filter(user_id=user_id).exclude(otp__isnull=True).exclude(otp=0).order_by('-created_at')
            serializer = BookingSerializer(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#Get My Profile
@api_view(['GET', 'PUT'])
def user_details(request):
    user_id = request.data.get('user_id') if request.method == 'PUT' else request.query_params.get('user_id')

    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UsersSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UsersSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Contact Form
class ContactFormView(APIView):
    def post(self, request):
        serializer = ContactFormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":"success","message": "Form submitted successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Recommended Best
class RecommendedProvidersView(APIView):
    def get(self, request):
        # Retrieve query parameters
        lat = request.query_params.get('latitude')
        lng = request.query_params.get('longitude')
        radius = float(request.query_params.get('radius', 50))  # Default radius 50 km
        service_type_id = request.query_params.get('service_type_id')  # Optional

        # Validate latitude and longitude
        if not lat or not lng:
            return Response(
                {
                    "status": "error",
                    "message": "Latitude and longitude are required.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Convert latitude and longitude to float
            lat = float(lat)
            lng = float(lng)

            # Haversine formula to calculate distance in km between two lat/lng points
            distance_expression = ExpressionWrapper(
                6371 * ACos(
                    Cos(Radians(lat))
                    * Cos(Radians(F("latitude")))
                    * Cos(Radians(F("longitude")) - Radians(lng))
                    + Sin(Radians(lat)) * Sin(Radians(F("latitude")))
                ),
                output_field=FloatField()
            )

            # Filter locations within the specified radius
            locations_within_radius = Locations.objects.annotate(
                distance_km=distance_expression
            ).filter(distance_km__lte=radius)

            # Filter service providers linked to the locations
            # providers_query = ServiceProvider.objects.filter(
            #     address_id__in=locations_within_radius
            # )
            #changed to branch
            # providers_query = Branches.objects.filter(
            #     location_id__in=locations_within_radius
            # ) 
            providers_query = Branches.objects.select_related("provider", "location").filter(
            location_id__in=locations_within_radius
                )  

            
            # Filter providers by service type, if specified
            if service_type_id:
                providers_query = providers_query.filter(provider__service_type=service_type_id)

            # Annotate provider query with location and other details
            # providers_query = providers_query.annotate(
            #     latitude=F("address__latitude"),
            #     longitude=F("address__longitude"),
            #     city=F("address__city"),
            #     state=F("address__state"),
            #     verified=Value(True, output_field=FloatField())
            # ).order_by("latitude")[:10]
            providers_query = providers_query.annotate(
                latitude=F("location__latitude"),
                longitude=F("location__longitude"),
                city=F("location__city"),
                state=F("location__state"),
                verified=Value(True, output_field=FloatField())
            ).order_by("latitude")[:10]

            # Get provider IDs
            provider_ids = providers_query.values_list('provider_id', flat=True)

            # Get dynamic rating and review count for each provider
            ratings = Review.objects.filter(provider_id__in=provider_ids).values(
                'provider_id'
            ).annotate(
                average_rating=Avg('rating'),
                review_count=Count('review_id')  # Count number of reviews for each provider
            )

            # Create a mapping of provider_id to its ratings and review count
            rating_map = {
                rating['provider_id']: {
                    'average_rating': rating['average_rating'],
                    'review_count': rating['review_count']
                }
                for rating in ratings
            }
            
            # Serialize provider data
            serializer = BranchSerializer(providers_query, many=True)

            # Add image URLs, ratings, and review counts to serialized data
            for provider in serializer.data:
                provider_id = provider.get('provider_id')

                # Append base URL to image URL
                if provider.get("image_url"):
                    # provider["image_url"] = f"{settings.BASE_URL}{provider['image_url']}"
                    provider["image_url"] = f"{provider['image_url']}"

                # Add the dynamic rating value
                provider["rating"] = round(rating_map.get(provider_id, {}).get('average_rating', 0), 1)

                # Format and add the review count
                review_count = rating_map.get(provider_id, {}).get('review_count', 0)
                provider["review_count"] = f"{review_count} review{'s' if review_count != 1 else ''}"

            # Return successful response
            return Response(
                {
                    "status": "success",
                    "message": "Providers retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            # Return error response
            return Response(
                {
                    "status": "error",
                    "message": "An error occurred while retrieving providers.",
                    "data": {"error": str(e)},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#SMS integration
class MindfulBeautySendSMS:
    def __init__(self):
        self.url = 'http://pay4sms.in'  # Base URL for the SMS API
        self.token = '8f897a8f86701c6b468439a91383527d'  # API Token
        self.credit = '2'  # Credit per SMS
        self.sender = 'MFBPLT'  # Sender ID for Mindful Beauty
        self.message_template = "Dear {name} , {otp} is the OTP for Login verification. Please do not share this code with anyone. Thank you for logging with us. mindfulbeauty.com"

    def send_sms(self, name, otp, numbers, validity=10):
        """
        Sends an SMS with the OTP to the specified phone number.

        Args:
            otp (str): The OTP to be sent.
            numbers (str): The recipient's phone number(s), comma-separated if multiple.
            validity (int): The validity period for the OTP in minutes.

        Returns:
            str: Response text from the SMS API.
        """
        message = self.message_template.format(name=name, otp=otp, validity=validity)
        message = requests.utils.quote(message)  # URL encode the message
        sms_url = f"{self.url}/sendsms/?token={self.token}&credit={self.credit}&sender={self.sender}&number={numbers}&message={message}"
        print(f"SMS API URL: {sms_url}")  # Log the full API URL for debugging
        response = requests.get(sms_url)
        return response.text

    def check_dlr(self, message_id):
        """
        Checks the delivery report (DLR) status for a specific message.

        Args:
            message_id (str): The message ID received from the SMS API.

        Returns:
            str: Response text from the SMS API for DLR status.
        """
        dlr_url = f"{self.url}/Dlrcheck/?token={self.token}&msgid={message_id}"
        response = requests.get(dlr_url)
        return response.text

    def available_credit(self):
        """
        Checks the available SMS credit balance.

        Returns:
            str: Response text from the SMS API for available credit balance.
        """
        credit_url = f"{self.url}/Credit-Balance/?token={self.token}"
        response = requests.get(credit_url)
        return response.text
    

#Cancel Booking 
class CancelBookingAPIView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        appointment_id = request.data.get('appointment_id')
        reason = request.data.get('reason')

        if not user_id or not appointment_id or not reason:
            return Response({"error": "User ID, Appointment ID, and Reason are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            appointment = Appointment.objects.get(appointment_id=appointment_id, user_id=user_id)

            # Convert appointment datetime to timezone-aware
            appointment_datetime = timezone.make_aware(
                timezone.datetime.combine(appointment.appointment_date, appointment.appointment_time),
                timezone.get_current_timezone()
            )

            # Calculate time difference correctly
            now = timezone.now()
            time_difference = appointment_datetime - now

            if time_difference < timedelta(hours=5):
                return Response({"error": "Cancellation is only allowed up to 5 hours before the appointment time."}, status=status.HTTP_400_BAD_REQUEST)

            # Update appointment status to 'Cancelled' and store reason
            appointment.status_id = 4  
            appointment.reason = reason
            appointment.save()

            return Response({"message": "Appointment cancelled successfully."}, status=status.HTTP_200_OK)

        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)