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

from .models import Review
from .serializers import ReviewSerializer

import random
import string

from datetime import datetime

from .models import Coupon
from .serializers import CouponSerializer

from .models import ServiceFAQ
from .serializers import ServiceFAQSerializer
from django.db import transaction
from decimal import Decimal
from django.db.models import Sum
from .models import Status


class LoginViewSet(viewsets.ModelViewSet):
    queryset = Login.objects.all()
    serializer_class = LoginSerializer

    # Override the `create` method for initiating login (generating OTP)
    def create(self, request, *args, **kwargs):
     phone = request.data.get('phone')  # Get phone number from request
 
     if not phone:
         return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
     
     # Check if the phone number exists in the User table
     if not User.objects.filter(phone=phone).exists():
         return Response({'status': 'failure', 'message': 'User not registered'}, status=status.HTTP_400_BAD_REQUEST)
 
     # Get or create the Login entry for the phone number
     login_entry, created = Login.objects.get_or_create(phone=phone)
     if created:
         # If entry was newly created, set OTP and timestamp
         login_entry.otp = '1234'  # Default OTP value
         login_entry.otp_created_at = timezone.now()
         login_entry.save()
         message = 'OTP generated and sent successfully'
     else:
         # If entry already existed, update OTP and timestamp
         login_entry.otp = '1234'  # Default OTP value
         login_entry.otp_created_at = timezone.now()
         login_entry.save()
         message = 'OTP updated successfully'
 
     # Return the OTP (In a real app, you'd send it via SMS)
     return Response({'status': 'success', 'otp': login_entry.otp, 'message': message}, status=status.HTTP_200_OK)

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
    queryset = ServiceTypes.objects.all()
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
                            image_url = base_url + settings.MEDIA_URL + str(provider.image_url)
                        
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
                serializer.save()  # Save the new user
                return Response({
                    'status': 'success',
                    'message': 'User created successfully',
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
            }, status=status.HTTP_404_NOT_FOUND)


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

class ServicesViewSet(viewsets.ModelViewSet):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer

    
    
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
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": "success",
                "message": "Categories retrieved successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failure",
                "message": "No categories found",
                "data": []
            },status=status.HTTP_404_NOT_FOUND)


class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "status": "success",
                "message": "Subcategories retrieved successfully",
                "data": serializer.data
            },
            status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failure",
                "message": "No subcategories found",
                "data": []
            },status=status.HTTP_404_NOT_FOUND)



class BookServiceViewSet(viewsets.ModelViewSet):
    queryset = Serviceprovidertype.objects.all()
    serializer_class = ServiceprovidertypeSerializer

    def list(self, request, *args, **kwargs):
        provider_id = request.query_params.get('provider_id')
        service_id= request.query_params.get('service_id')

        if not provider_id:
            return Response(
                {
                    "status": "failure",
                    "message": "Missing required query parameters: provider_id",
                    "data": []
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Fetching the details based on provider_id
            service_provider_type = Serviceprovidertype()
            provider_details = service_provider_type.get_provider_details(provider_id)
            provider_services = service_provider_type.get_provider_services(provider_id,service_id)
            beauticians = service_provider_type.get_beauticians_for_provider(provider_id) 
            provider_photos = service_provider_type.get_provider_photos(provider_id,0)
            provider_banner = service_provider_type.get_provider_photos(provider_id,1)
            faq = service_provider_type.get_faqs_for_provider(provider_id)
            overview = service_provider_type.get_overview_for_provider(provider_id)
            review=service_provider_type.get_reviews_by_provider(provider_id)
            packages = Serviceprovidertype().get_provider_packages(provider_id)

            return Response(
                {
                    "status": "success",
                    "message": "Filtered service provider types retrieved successfully",
                    "data": provider_details,
                    "services": provider_services,
                    "stylist": beauticians,
                    "photos": provider_photos,
                    "banner":provider_banner,
                    "faq": faq,
                    "overview": overview,
                    "review":review,
                    "packages":packages
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

    # Handle updating available slots
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.get('provider_id')
        
        # Validate that available slots are provided
        if not data:
            return Response({'error': 'Available slots data is required'}, status=status.HTTP_404_NOT_FOUND)
        
        instance.available_slots = data
        instance.save()
        
        return Response({'message': 'Available slots updated successfully', 'available_slots': instance.available_slots}, status=status.HTTP_200_OK)



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
            }, status=status.HTTP_200_OK)

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
            }, status=status.HTTP_200_OK)

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
                parsed_time = datetime.strptime(appointment_time, "%I:%M %p")  # 12-hour format with AM/PM
                appointment_time_24hr = parsed_time.strftime("%H:%M")  # Convert to 24-hour format
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

            # Check if an appointment already exists with the same user, provider, branch, date, and time
            existing_appointment = Appointment.objects.filter(
                user_id=user_id,
                provider_id=provider_id,
                branch_id=branch_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time_24hr,
                status=status_obj
            ).exists()

            if existing_appointment:
                return Response({"error": "You already have an appointment at this time."}, status=status.HTTP_200_OK)

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
        provider_id = request.query_params.get('provider_id')
        
        if not provider_id:
            return Response({"status": "error", "message": "Provider ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            provider_id = int(provider_id)
            now = datetime.now()

            bookings = Appointment.objects.filter(
                provider_id=provider_id,
                # status_id=0,  
                appointment_date__gte=now.date()  
            ).order_by('-appointment_date', '-appointment_time')  

            serializer = AppointmentSerializer(bookings, many=True)

            return Response(
                {"status": "success", "message": "Fetched successfully", "bookings": serializer.data},
                status=status.HTTP_200_OK
            )
        
        except ValueError:
            return Response({"status": "error", "message": "Invalid provider ID."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Provider booking action
class ProviderActionAPIView(APIView):
    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        action_id = request.data.get('action_id')  # Accepts action_id instead of action

        if not appointment_id or action_id is None:
            return Response(
                {"status": "error", "message": "Appointment ID and action_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Define the mapping for action_id to actions
            action_mapping = {
                1: "accept",
                2: "deny",
                3: "decline"
            }

            # Check if the provided action_id is valid
            action = action_mapping.get(action_id)
            if not action:
                return Response(
                    {"status": "error", "message": "Invalid action_id provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch the appointment
            appointment = Appointment.objects.get(appointment_id=appointment_id)

            # Handle actions based on action_id
            if action == "accept":
                appointment.status_id = 1  # 'schedule'
                appointment.otp = "1234"  # Generate or assign OTP here
                appointment.save()
                return Response(
                    {"status": "success", "message": "Appointment accepted and scheduled"},
                    status=status.HTTP_200_OK
                )

            elif action in ["deny", "decline"]:
                appointment.status_id = 4  # 'cancelled'
                appointment.otp = None  # No OTP sent for denial or decline
                appointment.save()
                return Response(
                    {"status": "success", "message": f"Appointment {action}d successfully"},
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

#Appointment status
class AppointmentStatusAPIView(APIView):
    def get(self, request):
        appointment_id = request.query_params.get('appointment_id')  # Get appointment_id from query parameters
        
        if not appointment_id:
            return Response(
                {"status": "error", "message": "Appointment ID is required"},
                status=status.HTTP_400_BAD_REQUEST
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
        """
        appointment_id = request.data.get("appointment_id")
        coupon_code = request.data.get("coupon_code", "")
        coupon_amount = request.data.get("coupon_amount", 0)
        amount = request.data.get("amount")  

        if not appointment_id or not amount:
            return Response({"error": "Appointment ID and amount are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            appointment = Appointment.objects.get(appointment_id=appointment_id)

            coupon_amount = Decimal(coupon_amount)
            amount = Decimal(amount)

            payment = Payment.objects.create(
                appointment=appointment,
                amount=amount,
                coupon_code=coupon_code,
                coupon_amount=coupon_amount,
                payment_status="Pending",
            )

            return Response({
                "message": "Payment recorded successfully",
                "payment_id": payment.payment_id,
                "amount": float(amount),
                "coupon_code": coupon_code,
                "coupon_amount": float(coupon_amount),
            }, status=status.HTTP_201_CREATED)

        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
