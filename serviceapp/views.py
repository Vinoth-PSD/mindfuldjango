from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from django.utils import timezone
from rest_framework.decorators import action
import random
import string
from .models import ServiceProvider,ProviderBankDetails,ProviderTaxRegistration,Role,Staff,Branches,Locations,Review,Category,Subcategory,Services,Serviceprovidertype,Permissions,Appointment,Status,Beautician,Payment,User,ProviderTransactions,AdminUser,Coupon,Message
from .serializers import LoginSerializer,ServiceProviderSerializer,ProviderBankDetailsSerializer,ProviderTaxRegistrationSerializer,SalonDetailsSerializer,FreelancerDetailsSerializer,RoleSerializer,StaffSerializer,StaffCreateSerializer,BranchSerializer,BranchesSerializer,BranchListSerializer,ReviewSerializer,ServicesSerializer,ServiceSerializer,PermissionsSerializer,CreatePermissionsSerializer,StatusSerializer,ServiceProvidersSerializer,CategorySerializer,SubcategorySerializer,BeauticianSerializer,ProviderTransactionSerializer,ReviewStatusSerializer,AddPackageServiceSerializer,PackagesSerializer,AdminUserSerializer,ProviderDetailsSerializer,AppointmentSerializer,SubcategoriesSerializer,ServicesSerializer,CouponSerializer,CouponsSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework import generics
from django.db.models import Q
from django.db import transaction
from collections import defaultdict
from django.http import JsonResponse
from datetime import datetime
import requests
import json  
from django.shortcuts import get_object_or_404
from django.db import connection
from django.db.models import F, Sum
from django.http import HttpResponse
from xhtml2pdf import pisa
import io
from django.template import Template, Context
from rest_framework import status as http_status
from decimal import Decimal
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
import razorpay
import hmac
import hashlib
from django.conf import settings
from django.utils.timezone import now




class LoginViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        phone = request.data.get('phone')  # Get phone number from request

        if not phone:
            return Response({'status': 'failure', 'message': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

        otp_target = None  # Initialize OTP target

        # Check if the phone number belongs to a ServiceProvider
        try:
            provider = ServiceProvider.objects.get(phone=phone, status="Active")
            otp_target = provider  # Set OTP target as provider
        except ServiceProvider.DoesNotExist:
            # If not found in ServiceProvider, check in Staff
            try:
                staff_entry = Staff.objects.get(phone=phone, is_deleted=False)
                
                # Ensure the provider associated with this staff has Active status
                if staff_entry.provider.status != "Active":
                    return Response({
                        "status": "failure",
                        "message": "Associated provider is not active"
                    }, status=status.HTTP_403_FORBIDDEN)

                otp_target = staff_entry  # Set OTP target as staff entry
            except Staff.DoesNotExist:
                return Response({
                    "status": "failure",
                    "message": "You don't have permission to login"
                }, status=status.HTTP_404_NOT_FOUND)

        # Generate 4-digit OTP
        otp = ''.join(random.choices(string.digits, k=4))
        
        # Save OTP and timestamp
        otp_target.otp = otp
        otp_target.otp_created_at = timezone.now()
        otp_target.save()

        # Send OTP via SMS
        sms = MindfulBeautySendSMS()
        provider_name = otp_target.name if isinstance(otp_target, ServiceProvider) else "User"
        sms_response = sms.send_sms(provider_name, otp, phone)

        print(sms_response)  # Debugging

        return Response({
            "status": "success",
            "otp": otp,
            "message": "OTP sent successfully"
        }, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request, *args, **kwargs):
        phone = request.data.get('phone')  # Get phone number from request
        otp = request.data.get('otp')  # Get OTP from request
    
        if not phone or not otp:
            return Response({'status': 'failure', 'message': 'Phone and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            # Check if the phone number belongs to a staff member
            staff_entry = Staff.objects.get(phone=phone, is_deleted=False)
            otp_target = staff_entry
            is_staff = True
        except Staff.DoesNotExist:
            # If not found in Staff, check in ServiceProvider
            try:
                service_provider = ServiceProvider.objects.get(phone=phone)
                otp_target = service_provider
                is_staff = False
            except ServiceProvider.DoesNotExist:
                return Response({'status': 'failure', 'message': 'Invalid phone number'}, status=status.HTTP_404_NOT_FOUND)
    
        # Check if the OTP matches
        if otp_target.otp == int(otp):
            # Generate a random token
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
    
            # Default permissions
            permissions_data_default = {
                'dashboard': True,
                'manage_role': True,
                'service_listing': True,
                'service_management': True,
                'sales_transactions': True,
                'ratings_reviews': True,
                'report_details': True,
                'roles_management': True,
                'staff_management': True,
                'branch_management': True,
                'all_booking': True,
                'schedule': True,
                'inprogress': True,
                'completed': True,
                'cancelled': True,
            }
    
            response_data = {
                'status': 'success',
                'message': 'Login successful',
                'token': token,
                'permissions': permissions_data_default,  # Default permissions initially
            }
    
            if is_staff:
                # Fetch provider and role information
                provider_entry = getattr(otp_target, 'provider', None)
                role_entry = getattr(otp_target, 'role', None)
    
                # Fetch permissions for the staff
                try:
                    permissions = Permissions.objects.get(role=role_entry, provider=provider_entry)
                    permissions_data = {
                        'dashboard': permissions.dashboard,
                        'manage_role': permissions.manage_role,
                        'service_listing': permissions.service_listing,
                        'service_management': permissions.service_management,
                        'sales_transactions': permissions.sales_transactions,
                        'ratings_reviews': permissions.ratings_reviews,
                        'report_details': permissions.report_details,
                        'roles_management': permissions.roles_management,
                        'staff_management': permissions.staff_management,
                        'branch_management': permissions.branch_management,
                        'all_booking': permissions.all_booking,
                        'schedule': permissions.schedule,
                        'inprogress': permissions.inprogress,
                        'completed': permissions.completed,
                        'cancelled': permissions.cancelled,
                    }
                except Permissions.DoesNotExist:
                    permissions_data = permissions_data_default  # Use default permissions if not found
                
    
            if is_staff:
                 # Fetch provider and role information
                 provider_entry = getattr(otp_target, 'provider', None)
                 role_entry = getattr(otp_target, 'role', None)
             
             
                 response_data.update({
                     'staff_id': otp_target.staff,
                     'role_id': role_entry.role_id if role_entry else None,
                     'role_name': role_entry.role_name if role_entry else None,
                     'provider_id': provider_entry.provider_id if provider_entry else None,
                     'permissions': permissions_data,
                 })

            else:
                # Update response for service provider
                response_data.update({
                    'provider_id': otp_target.provider_id,

                })
    
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'failure', 'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'], url_path='get-staff-permissions')
    def get_staff_permissions(self, request, *args, **kwargs):
            phone = request.data.get('phone')  # Get phone number from request
    
            if not phone:
                return Response({'status': 'failure', 'message': 'Phone number is required'}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # First, check if the phone number is associated with a staff member
            try:
                staff_entry = Staff.objects.get(phone=phone, is_deleted=False)
                provider_entry = staff_entry.provider  # Get the provider related to staff
                role_entry = staff_entry.role  # Get the role related to the staff
            except Staff.DoesNotExist:
                # If staff does not exist, check in the ServiceProvider table
                try:
                    provider_entry = ServiceProvider.objects.get(phone=phone)
                    # Now, fetch the staff entry associated with the provider if available
                    staff_entry = Staff.objects.filter(provider=provider_entry).first()
                    if not staff_entry:
                        return Response({'status': 'failure', 'message': 'No staff associated with this provider phone number'},
                                        status=status.HTTP_404_NOT_FOUND)
                    role_entry = staff_entry.role  # Get the role related to the staff
                except ServiceProvider.DoesNotExist:
                    return Response({'status': 'failure', 'message': 'Provided phone number does not exist in either staff or provider'},
                                    status=status.HTTP_404_NOT_FOUND)
    
            # Fetch permissions for the role of the staff
            try:
                permissions = Permissions.objects.get(role=role_entry, provider=provider_entry)
            except Permissions.DoesNotExist:
                # If permissions do not exist, we can either create them or return a failure
                return Response({'status': 'failure', 'message': 'Permissions not found for this role and provider'},
                                status=status.HTTP_404_NOT_FOUND)
    
            # Prepare the response with staff details and role permissions
            return Response({
                'status': 'success',
                'staff_id': staff_entry.staff,
                'provider_id': provider_entry.provider_id,
                'role_id': role_entry.role_id,
                'role_name': role_entry.role_name,
                'permissions': {
                    'dashboard': permissions.dashboard,
                    'manage_role': permissions.manage_role,
                    'service_listing': permissions.service_listing,
                    'service_management': permissions.service_management,
                    'sales_transactions': permissions.sales_transactions,
                    'ratings_reviews': permissions.ratings_reviews,
                    'report_details': permissions.report_details,
                    'roles_management': permissions.roles_management,
                    'staff_management': permissions.staff_management,
                    'branch_management': permissions.branch_management,
                    'all_booking': permissions.all_booking,
                    'schedule': permissions.schedule,
                    'inprogress': permissions.inprogress,
                    'completed': permissions.completed,
                    'cancelled': permissions.cancelled,
                }
            }, status=status.HTTP_200_OK)
        

    
#Registration        
class RegisterServiceProvider(APIView):
    def post(self, request):
        # Get the data from the request
        data = request.data

        # Validate the serializer
        serializer = ServiceProvidersSerializer(data=data)
        if serializer.is_valid():
            # Save the service provider
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Service Provider registered successfully!",
                    "data": serializer.data

                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": "failure",
                "message": "Service Provider with this phone number already exists.",
                "errors": serializer.errors
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
class ProviderGeneralInfo(APIView):
    def post(self, request, provider_id):
        try:
            # Fetch the ServiceProvider object using provider_id
            provider = ServiceProvider.objects.get(provider_id=provider_id)

            # Compare the foreign key ID instead of the object
            if provider.service_type_id == 1:
                serializer = SalonDetailsSerializer(provider, data=request.data, partial=True)
                print('data',serializer)
            elif provider.service_type_id == 2:
                serializer = FreelancerDetailsSerializer(provider, data=request.data, partial=True)
                print('data',serializer)
            else:
                return Response({"error": "Invalid service type!"}, status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                print('Serializer valid data:', serializer.validated_data)
                serializer.save()
                return Response(
                    {"message": "General information updated successfully!", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_200_OK)
        except ServiceProvider.DoesNotExist:
            return Response({"message": "Service Provider not found!"}, status=status.HTTP_404_NOT_FOUND)



        
class ProviderBankInfo(APIView):
    def post(self, request):
        provider_id = request.data.get('provider')

        if not ServiceProvider.objects.filter(provider_id=provider_id).exists():
            return Response({"error": "Provider not found."}, status=status.HTTP_400_BAD_REQUEST)

        existing_bank_details = ProviderBankDetails.objects.filter(provider_id=provider_id).first()

        if existing_bank_details:
            serializer = ProviderBankDetailsSerializer(existing_bank_details, data=request.data, partial=True)
        else:
            serializer = ProviderBankDetailsSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Bank details saved successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_200_OK)

    

class ProviderTaxInfo(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        provider_id = request.data.get('provider')

        if not ServiceProvider.objects.filter(provider_id=provider_id).exists():
            return Response({"error": "Provider not found."}, status=status.HTTP_400_BAD_REQUEST)

        existing_tax_registration = ProviderTaxRegistration.objects.filter(provider_id=provider_id).first()

        if existing_tax_registration:
            serializer = ProviderTaxRegistrationSerializer(existing_tax_registration, data=request.data, partial=True)
        else:
            serializer = ProviderTaxRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save tax registration details
            serializer.save()

            # Add default permissions after saving tax info
            self.add_default_permissions(provider_id)

            return Response({"message": "Tax registration details saved successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response({"error": serializer.errors}, status=status.HTTP_200_OK)

    def add_default_permissions(self, provider_id):
        try:
            # Fetch the provider
            provider = ServiceProvider.objects.get(provider_id=provider_id)

            # Default role ID; ensure you have a valid role ID
            role_id = 1  # Replace with actual role ID, you can also fetch it dynamically based on your logic
            
            # Check if permissions already exist for this provider
            if not Permissions.objects.filter(provider_id=provider_id).exists():
                permissions = Permissions(
                    role_id=role_id,  # Assign the correct role_id
                    provider_id=provider_id,
                    dashboard=True,
                    manage_role=True,
                    service_listing=True,
                    service_management=True,
                    sales_transactions=True,
                    ratings_reviews=True,
                    report_details=True,
                    roles_management=True,
                    staff_management=True,
                    branch_management=True,
                    all_booking=True,
                    schedule=True,
                    inprogress=True,
                    completed=True,
                    cancelled=True,
                )
                permissions.save()
                print(f"Permissions added for provider {provider_id}")

        except ServiceProvider.DoesNotExist:
            print(f"Provider with ID {provider_id} not found")

class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows roles to be viewed or edited.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = None  # Disable pagination at the view level

    def list(self, request, *args, **kwargs):
        # Fetch all roles
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Custom response format
        response_data = {
            "status": "success",
            "message": "Roles fetched successfully",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


#Staff Management
class StaffManagementAPIView(APIView):
    def get(self, request, provider_id=None):
        # Retrieve staff members filtered by provider_id if provided, and not marked as deleted
        if provider_id:
            staff_queryset = Staff.objects.filter(provider__provider_id=provider_id, is_deleted=False)
        else:
            staff_queryset = Staff.objects.filter(is_deleted=False)

        # Order staff members by `staff` ID in descending order
        staff_queryset = staff_queryset.order_by('-staff')

        # Implement search functionality
        search_query = request.query_params.get('search', None)
        if search_query:
            staff_queryset = staff_queryset.filter(name__icontains=search_query)  # Search by name

        # Paginate the queryset
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(staff_queryset, request)

        # Serialize the data
        serializer = StaffSerializer(paginated_queryset, many=True)

        # Return the paginated response
        return paginator.get_paginated_response({
            "status": "success",
            "data": serializer.data
        })

    def post(self, request):
        serializer = StaffCreateSerializer(data=request.data)
        if serializer.is_valid():
            staff = serializer.save()  # Create staff if data is valid
            return Response({
                "status": "success",
                "message": "Staff member added successfully.",
                "data": StaffCreateSerializer(staff).data
            }, status=status.HTTP_201_CREATED)
        else:
            # Return only the validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request):
       # Retrieve the staff_id from the request body
       staff_id = request.data.get("staff_id")
       if not staff_id:
           return Response({"status": "error", "message": "Staff ID is required."}, status=status.HTTP_400_BAD_REQUEST)
   
       try:
           # Retrieve the staff record
           staff = Staff.objects.get(staff=staff_id)
       except Staff.DoesNotExist:
           return Response({"status": "error", "message": "Staff not found."}, status=status.HTTP_404_NOT_FOUND)
   
       # Update the role field
       role_id = request.data.get("role")
       if role_id:
           try:
               role = Role.objects.get(role_id=role_id)
               staff.role = role
           except Role.DoesNotExist:
               return Response({"status": "error", "message": "Role not found."}, status=status.HTTP_400_BAD_REQUEST)
   
       # Update the provider field
       provider_id = request.data.get("provider")
       if provider_id:
           try:
               provider = ServiceProvider.objects.get(provider_id=provider_id)
               staff.provider = provider
           except ServiceProvider.DoesNotExist:
               return Response({"status": "error", "message": "Provider not found."}, status=status.HTTP_400_BAD_REQUEST)
   
       # Update the branch field
       branch_id = request.data.get("branch_id")
       if branch_id:
           try:
               branch = Branches.objects.get(branch_id=branch_id)
               staff.branch = branch
           except Branches.DoesNotExist:
               return Response({"status": "error", "message": "Branch not found."}, status=status.HTTP_400_BAD_REQUEST)
   
       # Update the photo field
       photo = request.FILES.get("photo")
       if photo:
           staff.photo = photo
   
       # Update other fields
       staff.name = request.data.get("name", staff.name)
       staff.phone = request.data.get("phone", staff.phone)
   
       # Save the updated staff record
       staff.save()
   
       return Response({"status": "success", "message": "Staff updated successfully."}, status=status.HTTP_200_OK)

    def delete(self, request):
        # Retrieve the staff_id from the request body
        staff_id = request.data.get("staff_id")
        if not staff_id:
            return Response({"status": "error", "message": "Staff ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the staff record
            staff = Staff.objects.get(staff=staff_id)
        except Staff.DoesNotExist:
            return Response({"status": "error", "message": "Staff not found."}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete: mark as deleted
        staff.is_deleted = True
        staff.save()

        return Response({"status": "success", "message": "Staff marked as deleted."}, status=status.HTTP_200_OK)
    
class StaffDetailAPIView(APIView):
    def get(self, request, staff_id):
        try:
            # Retrieve the staff record based on staff_id
            staff = Staff.objects.get(staff=staff_id, is_deleted=False)  
        except Staff.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Staff member not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the staff data
        serializer = StaffSerializer(staff)

        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

class BranchesByProviderAPIView(APIView):
    def get(self, request, provider_id):
        # Filter branches by provider_id and ensure is_deleted is False
        branches = Branches.objects.filter(provider_id=provider_id, is_deleted=False)

        if not branches.exists():
            return Response(
                {"status": "error", "message": "No active branches found for this provider."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize the data
        serializer = BranchSerializer(branches, many=True)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class CustomPagination(PageNumberPagination):
    page_size = 10  # You can set a default page size
    page_size_query_param = 'page_size'  # Clients can specify page size using ?page_size=20
    max_page_size = 100 


#Branch Management
class BranchListView(APIView):
    def get(self, request, provider_id=None):
        # Get the search parameter from the request
        search_query = request.query_params.get('search', None)

        # Retrieve branches filtered by provider_id if provided
        if provider_id:
            branch_queryset = Branches.objects.filter(
                provider__provider_id=provider_id,
                is_deleted=False
            ).order_by("-branch_id")  # Order by branch_id (recently added first)
        else:
            branch_queryset = Branches.objects.filter(
                is_deleted=False
            ).order_by("-branch_id")  # Order by branch_id (recently added first)

        # Apply search if a search query is provided
        if search_query:
            branch_queryset = branch_queryset.filter(
                Q(branch_name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(location__city__icontains=search_query)
            )

        # Serialize the data without pagination
        serializer = BranchListSerializer(branch_queryset, many=True)

        # Custom response format
        return Response({
            "status": "success",
            "message": "Branches fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class BranchListCreateView(APIView):
    def post(self, request):
        # Extract data from the request body
        branch_name = request.data.get('branch_name')
        phone = request.data.get('branch_phone_number')  # Get phone number from request
        branch_address = request.data.get('branch_address')  # This will contain address_line1
        branch_location = request.data.get('branch_location')  # This will contain city
        provider_id = request.data.get('provider_id')  # Required field
        logo = request.data.get('logo')
        latitude = request.data.get('latitude')  # Optional field
        longitude = request.data.get('longitude')  # Optional field

        # Validate `provider_id`
        if not provider_id:
            return Response(
                {"status": "failure", "message": "Provider ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            provider = ServiceProvider.objects.get(pk=provider_id)
        except ServiceProvider.DoesNotExist:
            return Response(
                {"status": "failure", "message": "Provider not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if both branch_address and branch_location are provided
        if not branch_address or not branch_location:
            return Response(
                {"status": "failure", "message": "Both branch_address and branch_location are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

         # Ensure location exists and retrieve its ID, including optional latitude & longitude
        location, created = Locations.objects.get_or_create(
            city=branch_location,
            address_line1=branch_address,
            defaults={
                "address_line2": "",
                "state": None,
                "postal_code": 0,
                "country": None,
                "latitude": latitude if latitude else None,
                "longitude": longitude if longitude else None,
            }
        )

        # If location already existed, update latitude & longitude if provided
        if not created and (latitude or longitude):
            location.latitude = latitude if latitude else location.latitude
            location.longitude = longitude if longitude else location.longitude
            location.save()

        # Prepare branch data with location_id and provider_id
        branch_data = {
            'branch_name': branch_name,
            'phone': phone,  # Ensure phone is passed correctly
            'logo': logo,
            'location': location.location_id,  # Pass the location_id here
            'provider_id': provider_id
        }

        # Use the serializer to save the branch data
        serializer = BranchesSerializer(data=branch_data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "message": "Branch created successfully!"},
                status=status.HTTP_201_CREATED
            )

        # If validation fails, return the errors
        return Response(
            {"status": "failure", "message": "Validation failed.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class BranchDetailView(APIView):
    def get_object(self, branch_id):
        try:
            return Branches.objects.get(branch_id=branch_id)
        except Branches.DoesNotExist:
            return None

    def get(self, request):
        # Retrieve `branch_id` from the request body
        branch_id = request.data.get("branch_id")
        if not branch_id:
            return Response({"status": "error", "error": "Branch ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        branch = self.get_object(branch_id)
        if not branch:
            return Response({"status": "error", "error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BranchListSerializer(branch)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request):
    # Retrieve `branch_id` from the request body
     branch_id = request.data.get("branch_id")
     if not branch_id:
         return Response({"status": "error", "error": "Branch ID is required."}, status=status.HTTP_400_BAD_REQUEST)
 
     branch = self.get_object(branch_id)
     if not branch:
         return Response({"status": "error", "error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)
 
     # Combine request data with any uploaded files
     data = request.data.copy()
     if request.FILES:
         data.update(request.FILES)
 
     # Update related location fields if provided
     if 'location' in data:
         city_name = data.get('location')
         try:
             # Retrieve the first location matching the city name
             location = Locations.objects.filter(city=city_name).first()
             if not location:
                 return Response(
                     {"status": "error", "error": f"Location with city name '{city_name}' not found."}, 
                     status=status.HTTP_400_BAD_REQUEST
                 )
             
             # Update location details if 'branch_address' is provided
             if 'branch_address' in data:
                 location.address_line1 = data.get('branch_address')
 
             # Update latitude and longitude if provided
             latitude = data.get('latitude')
             longitude = data.get('longitude')
 
             if latitude is not None:
                 location.latitude = latitude
             if longitude is not None:
                 location.longitude = longitude
 
             location.save()  # Save updated location
             
             # Use location_id for updating the branch
             data['location'] = location.location_id
         except Exception as e:
             return Response(
                 {"status": "error", "error": f"Error updating location: {str(e)}"}, 
                 status=status.HTTP_400_BAD_REQUEST
             )
 
     # Serialize and update branch
     serializer = BranchesSerializer(branch, data=data, partial=True)
     if serializer.is_valid():
         serializer.save()
         return Response(
             {"status": "success", "message": "Branch updated successfully!"}, 
             status=status.HTTP_200_OK
         )
     return Response(
         {"status": "error", "errors": serializer.errors}, 
         status=status.HTTP_400_BAD_REQUEST
     )




    def delete(self, request):
        # Retrieve `branch_id` from the request body
        branch_id = request.data.get("branch_id")
        if not branch_id:
            return Response({"status": "error", "error": "Branch ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        branch = self.get_object(branch_id)
        if not branch:
            return Response({"status": "error", "error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Perform soft delete
        branch.is_deleted = True
        branch.save()
        
        return Response({"status": "success", "message": "Branch deleted successfully!"}, status=status.HTTP_200_OK)




#Report & Rating
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination  # Use custom pagination

    def get_queryset(self):
        # Get provider_id from query parameters
        provider_id = self.request.query_params.get('provider_id')

        # Check if provider_id is provided, otherwise raise a validation error
        if not provider_id:
            raise ValidationError("provider_id is required")

        # Filter reviews based on provider_id
        reviews = Review.objects.filter(provider_id=provider_id).order_by('-created_at')  # Order by descending created_at

        # Add order_id (appointment_id) to reviews and map service_id_new to service objects
        for review in reviews:
            appointment = Appointment.objects.filter(provider_id=review.provider_id, user_id=review.user_id).first()
            if appointment:
                review.order_id = appointment.appointment_id

                # Get service objects from service_id_new
                service_ids = appointment.service_id_new.split(',')  # Assuming service IDs are stored as CSV
                service_objects = Services.objects.filter(service_id__in=service_ids)

                # Convert services to array of objects
                review.service_objects = [{"service_id": service.service_id, "service_name": service.service_name} for service in service_objects]

        return reviews



class ServicesViewSet(viewsets.ModelViewSet):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer

#Add Services
class AddServicesAPIView(APIView):
    def post(self, request):
        try:
            with transaction.atomic():
                # Extract data from the request
                provider_id = request.data.get('provider_id')
                branch_id = request.data.get('branch_id')
                category_id = request.data.get('category_id')
                subcategory_id = request.data.get('subcategory_id')
                service_ids_str = request.data.get('service_ids')  # Get service_ids as a string
                city = request.data.get('city', 'Kollam')  # Default to "Kollam" if city is not provided

                if not all([provider_id, branch_id, category_id, subcategory_id, service_ids_str]):
                    return Response(
                        {'status_code': 0, 'status': 'failure', 'message': 'Missing required fields'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Convert the service_ids string into a list of integers
                try:
                    service_ids = [int(service_id.strip()) for service_id in service_ids_str.split(',')]
                except ValueError:
                    return Response(
                        {'status_code': 0, 'status': 'failure', 'message': 'Invalid service_ids format'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Initialize a list to store the provider_service_ids
                provider_service_ids = []

                # Loop through selected services and add/update them in Serviceprovidertype
                for service_id in service_ids:
                    try:
                        # Fetch the service from the Services table by primary key
                        service = Services.objects.get(service_id=service_id)

                        # Check if the service already exists for the provider and branch
                        service_provider_type, created = Serviceprovidertype.objects.update_or_create(
                            provider_id_id=provider_id,
                            branch_id=branch_id,
                            service_id_id=service_id,
                            defaults={
                                'price': service.price,  # Update the price from Services
                                'duration': service.service_time,  # Update the duration from Services
                                'status': 'Active'
                            }
                        )
                        # Append the provider_service_id to the list
                        provider_service_ids.append(service_provider_type.provider_service_id)
                    except Services.DoesNotExist:
                        return Response(
                            {'status_code': 0, 'status': 'failure', 'message': f'Service with ID {service_id} not found'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                    except Exception as e:
                        return Response(
                            {'status_code': 0, 'status': 'failure', 'message': f'Error adding/updating service: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

                # Fetch the newly added/updated services from Serviceprovidertype
                added_services = Serviceprovidertype.objects.filter(provider_service_id__in=provider_service_ids)

                # Prepare a response with added/updated services details
                services_data = []
                for service_provider in added_services:
                    service = service_provider.service_id
                    services_data.append({
                        'sku_id': service.sku_value,
                        'service_name': service.service_name,
                        'category': service.category.category_name if service.category else None,
                        'subcategory': service.subcategory.subcategory_name if service.subcategory else None,
                        'price': service_provider.price,
                        'duration': service_provider.duration,  # Return duration as a string
                        'status': service_provider.status
                    })

                # Return the success response with all provider_service_ids and the added/updated services details
                return Response(
                    {
                        'status_code': 1,
                        'status': 'success',
                        'message': 'Services added/updated successfully',
                        'provider_service_ids': provider_service_ids,
                        'added_services': services_data
                    },
                    status=status.HTTP_201_CREATED
                )

        except Exception as e:
            return Response(
                {'status_code': 0, 'status': 'failure', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#Active services
class ActiveServicesView(APIView):
    def get(self, request, *args, **kwargs):
        provider_id = request.query_params.get("provider_id")
        branch_id = request.query_params.get("branch_id")  

        # Validate required parameters
        if not provider_id:
            return Response({"error": "provider_id is required"}, status=400)

        response_data = []
        categories = Category.objects.filter(status="Active")

        for category in categories:
            category_data = {
                "category_id": category.category_id,
                "category": category.category_name,
                "subcategories": []
            }

            subcategories = Subcategory.objects.filter(category=category, status="Active")

            for subcategory in subcategories:
                # Build the filter criteria dynamically
                filter_criteria = {
                    "service_id__category": category,
                    "service_id__subcategory": subcategory,
                    "provider_id": provider_id,
                    "status": "Active",
                    "is_deleted": False,  
                }
                if branch_id:  # Add branch filter only if branch_id is provided
                    filter_criteria["branch"] = branch_id

                # Query the Serviceprovidertype table for active services
                recent_service_providers = (
                    Serviceprovidertype.objects.filter(**filter_criteria)
                    .order_by("-provider_service_id")[:100]  # Fetch the most recent 100 services
                )

                # Skip subcategories with no services
                if not recent_service_providers.exists():
                    continue

                # Prepare subcategory data
                subcategory_data = {
                    "subcategory_id": subcategory.subcategory_id,
                    "subcategory": subcategory.subcategory_name,
                    "services": [
                        {
                            "provider_service_id": service.provider_service_id,  # Add provider_service_id
                            "service_id": service.service_id.service_id,
                            "service_name": service.service_id.service_name,
                            "sku_value": service.service_id.sku_value,
                            "price": service.price,
                            "service_time": service.duration,
                            "is_deleted": service.is_deleted,  

                        }
                        for service in recent_service_providers
                    ],
                }

                # Add subcategory data to the category
                category_data["subcategories"].append(subcategory_data)

            # Skip categories with no subcategories
            if not category_data["subcategories"]:
                continue

            # Add category data to the response
            response_data.append(category_data)

        return Response(response_data, status=200)
    
#copyservices
class CopyBranchServicesAPIView(APIView):
    def post(self, request):
        try:
            with transaction.atomic():
                # Extract data from the request
                source_branch_id = request.data.get("source_branch_id")
                target_branch_ids = request.data.get("target_branch_id")  # Comma-separated string
                provider_id = request.data.get("provider_id")  # Optional field

                # Validate required parameters
                if not all([source_branch_id, target_branch_ids]):
                    return Response(
                        {"status_code": 0, "status": "failure", "message": "Missing required fields"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if source_branch_id == target_branch_ids:
                    return Response(
                        {"status_code": 0, "status": "failure", "message": "Source and target branches cannot be the same"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Convert the comma-separated target_branch_ids to a list of integers
                try:
                    target_branch_ids = [int(branch_id.strip()) for branch_id in target_branch_ids.split(',')]
                except ValueError:
                    return Response(
                        {"status_code": 0, "status": "failure", "message": "Invalid target branch ID format"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Fetch all active services for the source branch
                services_to_copy = Serviceprovidertype.objects.filter(
                    branch_id=source_branch_id,
                    status="Active",
                    is_deleted=False,
                )

                if not services_to_copy.exists():
                    return Response(
                        {"status_code": 0, "status": "failure", "message": "No services found in the source branch"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Fetch the ServiceProvider instance if provider_id is provided
                provider_instance = None
                if provider_id:
                    try:
                        provider_instance = ServiceProvider.objects.get(provider_id=provider_id)
                    except ServiceProvider.DoesNotExist:
                        return Response(
                            {"status_code": 0, "status": "failure", "message": "Invalid provider_id"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                # Create a list to store copied services
                copied_service_ids = []

                # Loop through the services and copy them to the target branches
                for service in services_to_copy:
                    defaults = {
                        "price": service.price,
                        "duration": service.duration,
                        "status": "Active",
                    }

                    # Include the provider_instance in defaults if it's provided
                    if provider_instance:
                        defaults["provider_id"] = provider_instance

                    # Instead of using update_or_create(), use filter to ensure unique records per branch-service pair
                    for target_branch_id in target_branch_ids:
                        # Check if a Serviceprovidertype with the same branch_id and service_id already exists
                        existing_service = Serviceprovidertype.objects.filter(
                            branch_id=target_branch_id,
                            service_id=service.service_id
                        ).first()  # Use first() to ensure only one instance is fetched

                        if existing_service:
                            # If it exists, update it
                            existing_service.price = service.price
                            existing_service.duration = service.duration
                            existing_service.status = "Active"
                            if provider_instance:
                                existing_service.provider_id = provider_instance
                            existing_service.save()
                            copied_service_ids.append(existing_service.provider_service_id)
                        else:
                            # Otherwise, create a new one
                            new_service = Serviceprovidertype.objects.create(
                                branch_id=target_branch_id,
                                service_id=service.service_id,
                                price=service.price,
                                duration=service.duration,
                                status="Active",
                                provider_id=provider_instance if provider_instance else None
                            )
                            copied_service_ids.append(new_service.provider_service_id)

                # Fetch the newly added/updated services for the target branches
                copied_services = Serviceprovidertype.objects.filter(provider_service_id__in=copied_service_ids)

                # Prepare a response with copied services details
                services_data = [
                    {
                        "provider_service_id": service.provider_service_id,
                        "service_id": service.service_id.service_id,
                        "service_name": service.service_id.service_name,
                        "sku_value": service.service_id.sku_value,
                        "price": service.price,
                        "service_time": service.duration,
                        "status": service.status,
                        "provider_id": service.provider_id.provider_id if service.provider_id else None,
                    }
                    for service in copied_services
                ]

                return Response(
                    {
                        "status_code": 1,
                        "status": "success",
                        "message": "Services copied successfully",
                        "copied_services": services_data,
                    },
                    status=status.HTTP_201_CREATED,
                )
        except Exception as e:
            return Response(
                {"status_code": 0, "status": "failure", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


#Service List
class ProviderServicesView(APIView):
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['provider_id__name',  'service_id__service_name','service_id__category__category_name',  'service_id__subcategory__subcategory_name',  'price', 'duration', 'status', 'branch__branch_name']
    def get(self, request):
        provider_id = request.query_params.get('provider_id', None)
        branch_id = request.query_params.get('branch_id', '0')  # Default to '0' if not provided

        # Validate that provider_id is provided
        if not provider_id:
            return Response(
                {"error": "'provider_id' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Convert branch_id to integer, default to 0 if not provided
            branch_id = int(branch_id)

            # Filter services based on provider_id and optionally branch_id
            filters = {"provider_id": provider_id, "is_deleted": False}
            if branch_id != 0:  # Only apply branch_id filter if it's not 0
                filters["branch_id"] = branch_id

            # Order services by `id` in descending order (recently added first)
            services = (
                Serviceprovidertype.objects.filter(**filters)
                .order_by('service_id', '-provider_service_id')  # The `service_id` must be the first field in `order_by`
                .distinct('service_id')  # Ensure unique services by `service_id`
            )


            # If no services are found, return a message
            if not services.exists():
                return Response({
                    "count": 0,
                    "next": None,
                    "previous": None,
                    "results": [],
                    "message": "No services found for the given provider and branch."
                }, status=status.HTTP_200_OK)

            # Apply search filter
            for backend in list(self.filter_backends):
              services = backend().filter_queryset(request, services, self)

            # Apply pagination
            paginator = CustomPagination()
            result_page = paginator.paginate_queryset(services, request)
            if result_page is not None:
                serialized_data = self.serialize_services(result_page)
                response = paginator.get_paginated_response(serialized_data).data
                response["message"] = "Services retrieved successfully."
                return Response(response, status=status.HTTP_200_OK)

            # In case pagination is not applied
            return Response({
                "count": services.count(),
                "next": None,
                "previous": None,
                "results": self.serialize_services(services),
                "message": "Services retrieved successfully."
            }, status=status.HTTP_200_OK)

        except Serviceprovidertype.DoesNotExist:
            return Response({"error": "No services found for the given provider."}, status=status.HTTP_404_NOT_FOUND)

    def serialize_services(self, services):
        """
        Serializes the list of services with category_id and subcategory_id.
        Checks if duration and price exist in Serviceprovidertype, otherwise uses Services.
        """
        service_data = []
        for service_provider in services:
            service = service_provider.service_id

            # Check if price and duration are available in Serviceprovidertype
            price = service_provider.price if service_provider.price else service.price
            duration = service_provider.duration if service_provider.duration else service.service_time

            service_data.append({
                'provider_service_id': service_provider.provider_service_id,  
                'service_id': service.service_id,
                'service_name': service.service_name,
                'category': service.category.category_name if service.category else None,
                'category_id': service.category.category_id if service.category else None,  # Adding category_id
                'subcategory': service.subcategory.subcategory_name if service.subcategory else None,
                'subcategory_id': service.subcategory.subcategory_id if service.subcategory else None,  # Adding subcategory_id
                'price': price,  # Price from Serviceprovidertype or Services
                'duration': duration,  # Duration from Serviceprovidertype or Services
                'status': service_provider.status,
                'sku_value': service.sku_value,
                'branch_id': service_provider.branch_id  
            })
        return service_data


#Update Services   
class UpdateActiveServicesView(APIView):
    def put(self, request):
        try:
            with transaction.atomic():
                # Extract and parse data from the request
                services_data = request.data.get('services')

                # Check if 'services' is a string and convert it to a list
                if isinstance(services_data, str):
                    services_data = json.loads(services_data)

                if not services_data:
                    return Response(
                        {'status': 'failure', 'message': 'No services provided for update'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Loop through each service and update the details
                for service_data in services_data:
                    service_id = service_data.get('id')
                    price = service_data.get('price')
                    duration = service_data.get('duration')
                    is_deleted = service_data.get('is_deleted', False)  # Default to `False`

                    # Validate service ID
                    if not service_id:
                        return Response(
                            {'status': 'failure', 'message': 'Service ID is required'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Update or delete the service details
                    try:
                        service = Serviceprovidertype.objects.get(provider_service_id=service_id)
                        if is_deleted:
                            service.is_deleted = True
                        else:
                            if price is not None:
                                service.price = price
                            if duration is not None:
                                service.duration = duration
                        service.save()
                    except Serviceprovidertype.DoesNotExist:
                        return Response(
                            {'status': 'failure', 'message': f'Service with ID {service_id} not found'},
                            status=status.HTTP_404_NOT_FOUND
                        )

                return Response(
                    {'status': 'success', 'message': 'Services updated successfully'},
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {'status': 'failure', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
#Edit service     
class EditServiceAPIView(APIView):
    def put(self, request):
        try:
            with transaction.atomic():
                # Extract provider_service_id from the request body
                provider_service_id = request.data.get("provider_service_id")
                if not provider_service_id:
                    return Response(
                        {"status": "failure", "message": "Provider service ID is required."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Extract data from the request
                price = request.data.get("price")
                duration = request.data.get("duration")
                status_value = request.data.get("status")  # Avoid conflict with `status` module

                # Validate the input data
                if price is None and duration is None and status_value is None:
                    return Response(
                        {"status": "failure", "message": "No fields to update."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Fetch the Serviceprovidertype object
                service = Serviceprovidertype.objects.filter(
                    provider_service_id=provider_service_id, is_deleted=False
                ).first()

                if not service:
                    return Response(
                        {"status": "failure", "message": "Service not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # Update the service fields if provided
                if price is not None:
                    service.price = price
                if duration is not None:
                    service.duration = duration
                if status_value is not None:
                    service.status = status_value

                # Save the updated service
                service.save()

                return Response(
                    {"status": "success", "message": "Service updated successfully."},
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {"status": "failure", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


#Delete service
class DeleteServiceAPIView(APIView):
    def delete(self, request):
        try:
            # Extract provider_service_id from the request body
            provider_service_id = request.data.get("provider_service_id")
            if not provider_service_id:
                return Response(
                    {"status": "failure", "message": "Provider service ID is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch the Serviceprovidertype object
            service = Serviceprovidertype.objects.filter(provider_service_id=provider_service_id).first()

            if not service:
                return Response(
                    {"status": "failure", "message": "Service not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Mark as deleted and update status
            service.is_deleted = True
            service.status = "Inactive"
            service.save()

            return Response(
                {"status": "success", "message": "Service marked as deleted successfully."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "failure", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        
#Role management
class PermissionsAPIView(APIView):
    def post(self, request):
        provider_id = request.data.get('provider')
        role_id = request.data.get('role')

        # Define the list of boolean-like fields
        boolean_fields = [
            "dashboard", "manage_role", "service_listing", "service_management", 
            "sales_transactions", "ratings_reviews", "report_details", 
            "roles_management", "staff_management", "branch_management", 
            "all_booking", "schedule", "inprogress", "completed", "cancelled"
        ]

        # Convert "true"/"false" strings to the appropriate TEXT values
        for field in boolean_fields:
            if field in request.data:
                value = request.data[field]
                if isinstance(value, str):
                    request.data[field] = "true" if value.lower() == "true" else "false"

        # Check if an existing permission exists for the given provider and role
        permission = Permissions.objects.filter(provider_id=provider_id, role_id=role_id).first()

        if permission:
            # Update existing permission
            serializer = PermissionsSerializer(permission, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'status': 'success', 'message': 'Permissions updated successfully!'},
                    status=status.HTTP_200_OK
                )
            return Response({'status': 'failure', 'errors': serializer.errors}, status=status.HTTP_200_OK)
        else:
            # Create a new permission
            serializer = CreatePermissionsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'status': 'success', 'message': 'Permissions added successfully!'},
                    status=status.HTTP_201_CREATED
                )
            return Response({'status': 'failure', 'errors': serializer.errors}, status=status.HTTP_200_OK)


class RoleProviderPermissionsAPIView(APIView):
    def get(self, request, provider_id):
        # Retrieve all permissions related to the provider
        permissions = Permissions.objects.filter(provider_id=provider_id)

        if permissions.exists():
            # Serialize and return the data if found
            serializer = PermissionsSerializer(permissions, many=True)
            return Response(
                {
                    'status': 'success',
                    'message': 'Permissions retrieved successfully!',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'status': 'failure',
                'message': 'No permissions found for this provider.'
            },
            status=status.HTTP_200_OK
        )


#Appointment list 
class AppointmentListView(APIView):
    """
    API to list appointments for a given provider_id and optional status
    """

    def get(self, request, *args, **kwargs):
        provider_id = request.GET.get('provider_id')
        status_filter = request.GET.get('status')  # Get optional status filter
        search_query = request.GET.get('search', '')  # Optional search query

        # Ensure provider_id is provided
        if not provider_id:
            return JsonResponse(
                {"status": "error", "message": "provider_id is required"},
                status=400
            )

        # Filter appointments based on provider_id and optional status filter
        if status_filter:
            appointments = Appointment.objects.filter(
                provider_id=provider_id,
                status__status_id=status_filter
            ).select_related('branch__location').order_by('-appointment_id')
        else:
            appointments = Appointment.objects.filter(
                provider_id=provider_id
            ).select_related('branch__location').order_by('-appointment_id')

        if search_query:
            # Get matching service IDs
            matching_service_ids = Services.objects.filter(
                Q(service_name__icontains=search_query) |
                Q(price__icontains=search_query)
            ).values_list('service_id', flat=True)  # Extract IDs

            # Convert matching service IDs into a list of strings (to match text field)
            matching_service_ids = [str(service_id) for service_id in matching_service_ids]

            # Build the search filter
            appointments = appointments.filter(
                Q(user__name__icontains=search_query) |
                Q(user__phone__icontains=search_query) |
                Q(stylist__name__icontains=search_query) |
                Q(status__status_name__icontains=search_query) |
                Q(branch__location__city__icontains=search_query) |
                Q(appointment_date__icontains=search_query) |
                Q(appointment_time__icontains=search_query) |
                Q(service_id_new__icontains=search_query) |  # Search raw text for IDs
                Q(service_id_new__regex=r'(^|,)' + '|'.join(matching_service_ids) + r'(,|$)')  # Match whole service IDs
            )

        # Paginate the results
        paginator = CustomPagination()
        paginated_appointments = paginator.paginate_queryset(appointments, request)

        # Serialize data into JSON-friendly format
        data = []
        for appointment in paginated_appointments:
            # Initialize service_ids safely
            service_ids = []
            if appointment.service_id_new:
                service_ids = appointment.service_id_new.split(",")

            # Fetch the services from the database
            services = Services.objects.filter(service_id__in=service_ids)

            # Serialize service details into an array of arrays
            service_details = [
                {"service_id": service.service_id, "name": service.service_name, "price": float(service.price) if service.price else 0}
                for service in services
            ]

            # Calculate the total amount
            total_amount = sum(float(service["price"]) for service in service_details)

            # Check payment table for appointment total
            payment = Payment.objects.filter(appointment=appointment).first()
            if payment:
                total_amount = float(payment.grand_total) if payment.grand_total else total_amount

            # Format the date as '10 Dec 2024'
            try:
                formatted_date = datetime.strptime(str(appointment.appointment_date), "%Y-%m-%d").strftime("%d %b %Y")
                formatted_time = datetime.strptime(str(appointment.appointment_time), "%H:%M:%S").strftime("%H:%M")
            except ValueError:
                # Handle the case where the date or time format is incorrect
                formatted_date = str(appointment.appointment_date)  # Fallback to string if error
                formatted_time = str(appointment.appointment_time)  # Fallback to string if error

            # Get the city name from the Location table using the branch_id
            city = None
            if appointment.branch:
                try:
                    # Use select_related to avoid repeated queries when accessing branch and location
                    location = appointment.branch.location
                    city = location.city if location else None
                except Branches.DoesNotExist:
                    # Handle case where branch does not exist (i.e., appointment with invalid branch_id)
                    city = None

            # Get stylist details
            stylist_name = None
            stylist_id = None
            if appointment.stylist:
                stylist_name = appointment.stylist.name
                stylist_id = appointment.stylist.staff  

            # Safely fetch the status name
            status_name = appointment.status.status_name if hasattr(appointment, 'status') and appointment.status else "No Status"

            # Fetch payment status for the appointment
            payment_status = payment.payment_status if payment else "Not Paid"

            # Append serialized data
            data.append({
                "id": appointment.appointment_id,
                "date": formatted_date,  
                "time": formatted_time,  
                "name": appointment.user.name,
                "phone": appointment.user.phone,
                "services": service_details,  # Array of service details
                "amount": total_amount, 
                "status": status_name,  # Get status name from Status model
                "status_id": appointment.status.status_id if hasattr(appointment, 'status') and appointment.status else None,  
                "modify_status": status_name,
                "location": city,  
                "stylist": stylist_name, 
                "stylist_id": stylist_id,
                "payment_status": payment_status  
            })

        # Return paginated response
        return paginator.get_paginated_response(data)



#Modify status
class ModifyAppointmentStatus(APIView):
    def put(self, request, *args, **kwargs):
        appointment_id = request.data.get("appointment_id")
        status_id = request.data.get("status_id")
        stylist_id = request.data.get("stylist_id")

        # Validate required appointment_id input
        if not appointment_id:
            return Response(
                {"status": "failure", "message": "appointment_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the appointment
        appointment = get_object_or_404(Appointment, appointment_id=appointment_id)

        # Only update status if status_id is provided
        if status_id:
            new_status = get_object_or_404(Status, status_id=status_id)
            appointment.status = new_status

        # If stylist_id is provided, update the stylist
        if stylist_id:
            stylist = get_object_or_404(Staff, staff=stylist_id)
            appointment.stylist = stylist

        # Save the updated appointment
        appointment.save()

        return Response(
            {"status": "success", "message": "Appointment status updated successfully."},
            status=status.HTTP_200_OK
        )

#Appointment update     
class AppointmentUpdateStatusView(APIView):
    """
    API to update the status of an appointment.
    """

    def post(self, request, *args, **kwargs):
        appointment_id = request.data.get('appointment_id')
        new_status = request.data.get('status')  # Expected to be '1' for acceptance

        if not appointment_id or new_status is None:
            return JsonResponse(
                {"status": "error", "message": "appointment_id and status are required"},
                status=400
            )

        try:
            # Fetch the appointment record
            appointment = Appointment.objects.get(appointment_id=appointment_id)
            
            # Update the status
            appointment.status_id = int(new_status)  # Ensure the new status is an integer
            appointment.save()

            return JsonResponse(
                {"status": "success", "message": f"Appointment {appointment_id} status updated to {new_status}"},
                status=200
            )
        except Appointment.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": f"Appointment with id {appointment_id} does not exist"},
                status=404
            )
        except ValueError:
            return JsonResponse(
                {"status": "error", "message": "Invalid status value. It must be an integer."},
                status=400
            )


#status   
class StatusViewSet(viewsets.ModelViewSet):
    """
    API to list all statuses without pagination.
    """
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    pagination_class = None  # Disable pagination

    def list(self, request, *args, **kwargs):
        statuses = self.get_queryset()
        serializer = self.get_serializer(statuses, many=True)
        return Response(serializer.data)
    
#category    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_deleted=False).order_by('-category_id')
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
        

#subcategory
class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.filter(is_deleted=False).order_by('-subcategory_id')
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        """
        Optionally filters subcategories by category_id.
        """
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id', None)

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

#Services         
class ServicesByCategorySubcategoryView(APIView):
    def get(self, request):
        # Get category_id and subcategory_id from query parameters
        category_id = request.query_params.get('category_id', None)
        subcategory_id = request.query_params.get('subcategory_id', None)

        # Validate that both parameters are provided
        if not category_id or not subcategory_id:
            return Response(
                {"error": "'category_id' and 'subcategory_id' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Filter services by both category_id and subcategory_id
        services = Services.objects.filter(
            category_id=category_id,
            subcategory_id=subcategory_id,
            status='Active'
        )

        # If no services are found
        if not services.exists():
            return Response(
                {"message": "No services found for the given category and subcategory."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Prepare response data with only service_id and service_name
        data = [
            {
                "service_id": service.service_id,
                "service_name": service.service_name,
            }
            for service in services
        ]

        return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)

#stylist   
class BeauticianViewSet(viewsets.ModelViewSet):
    """
    API to fetch stylist names based on provider_id with status and message.
    """
    def get_serializer_class(self):
        return BeauticianSerializer

    def list(self, request):
        provider_id = request.query_params.get('provider_id', None)

        if not provider_id:
            return Response(
                {
                    "status": "error",
                    "message": "'provider_id' is required.",
                    "data": []
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        beauticians = Beautician.objects.filter(provider_id=provider_id)

        if not beauticians.exists():
            return Response(
                {
                    "status": "success",
                    "message": "No stylists found for the given provider.",
                    "data": []
                },
                status=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(beauticians, many=True)
        return Response(
            {
                "status": "success",
                "message": "Stylist(s) retrieved successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK,
        )

#Assign stylist in appointment table
class AssignStylistView(APIView):
    """
    API to assign a stylist to an appointment
    """
    def put(self, request, *args, **kwargs):
        # Get appointment ID and stylist ID from the request
        appointment_id = request.data.get('appointment_id')
        stylist_id = request.data.get('stylist_id')

        if not appointment_id or not stylist_id:
            return Response(
                {"status": "error", "message": "appointment_id and stylist_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the appointment and stylist existence
        appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
        stylist = get_object_or_404(Beautician, id=stylist_id)

        # Assign the stylist to the appointment
        appointment.stylist = stylist
        appointment.save()

        return Response(
            {"status": "success", "message": f"Stylist {stylist.name} has been assigned to the appointment."},
            status=status.HTTP_200_OK
        )

#Sales and Transactions
class SalesTransactionAPIView(APIView, CustomPagination):
    def get(self, request):
        provider_id = request.query_params.get('provider_id')
        appointment_id = request.query_params.get('appointment_id')
        customer_query = request.query_params.get('customer_query')  # Can be customer_name or mobile_number
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        branch_query = request.query_params.get('branch_query')  # Can be branch_name or branch_phone

        if not provider_id:
            return JsonResponse({"error": "Provider ID is required"}, status=400)

        query = """
            SELECT 
                a.appointment_id AS order_id,
                a.appointment_date,
                u.name AS user_name,
                u.phone,
                a.service_id_new,
                p.amount,
                p.sgst,
                p.cgst,
                p.grand_total,
                p.payment_mode,
                p.payment_status AS paystatus,
                s.status_name AS appointment_status,
                loc.city,
                b.branch_name,
                b.phone AS branch_phone
            FROM beautyapp_payment p
            INNER JOIN beautyapp_appointment a ON p.appointment_id = a.appointment_id
            INNER JOIN beautyapp_user u ON a.user_id = u.user_id
            INNER JOIN beautyapp_status s ON a.status_id = s.status_id
            LEFT JOIN branches b ON a.branch_id = b.branch_id
            LEFT JOIN locations loc ON b.location_id = loc.location_id
            WHERE a.provider_id = %s
        """
        params = [provider_id]

        if appointment_id:
            query += " AND a.appointment_id = %s"
            params.append(appointment_id)

        if customer_query:
            if customer_query.isdigit():  # If numeric, assume it's a phone number
                query += " AND u.phone LIKE %s"
                customer_query = f"%{customer_query}%"  # Enable partial matching
            else:  # Otherwise, assume it's a name
                query += " AND u.name ILIKE %s"
                customer_query = f"%{customer_query}%"
            params.append(customer_query)

        if start_date:
            query += " AND a.appointment_date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND a.appointment_date <= %s"
            params.append(end_date)

        if branch_query:
            if branch_query.isdigit():  # If numeric, assume it's a phone number
                query += " AND b.phone LIKE %s"
                branch_query = f"%{branch_query}%"
            else:  # Otherwise, assume it's a branch name
                query += " AND b.branch_name ILIKE %s"
                branch_query = f"%{branch_query}%"
            params.append(branch_query)

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        data = []
        for row in rows:
            service_ids = row[4].split(',') if row[4] else []
            services = []

            if service_ids:
                with connection.cursor() as service_cursor:
                    service_query = """
                        SELECT service_name 
                        FROM beautyapp_services 
                        WHERE service_id IN %s
                    """
                    service_cursor.execute(service_query, [tuple(service_ids)])
                    services = [service[0] for service in service_cursor.fetchall()]

            data.append({
                "order_id": row[0],
                "appointment_date": row[1],
                "city": row[12],
                "user_name": row[2],
                "phone": row[3],
                "services": ", ".join(services),
                "amount": float(row[5]),
                "sgst": row[6],
                "cgst": row[7],
                "total": row[8],
                "paymode": row[9],
                "paystatus": row[10],
                "appointment_status": row[11],
                "branch_name": row[13],
                "branch_phone": row[14],
            })

        paginated_data = self.paginate_queryset(data, request, view=self)
        return self.get_paginated_response(paginated_data)



   

# Get Invoice list
def get_invoice_view(request):
    try:
        # Get appointment_id from query parameters
        appointment_id = request.GET.get('appointment_id')
        if not appointment_id:
            return JsonResponse({'status': 'error', 'message': 'appointment_id is required'}, status=400)
        
        # Fetch appointment details
        appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
        
        # Fetch user details
        user = get_object_or_404(User, user_id=appointment.user.user_id)
        
        # Fetch payment details
        payment = get_object_or_404(Payment, appointment=appointment)
        
        # Get service IDs and fetch services
        service_ids = map(int, appointment.service_id_new.split(','))  # Convert comma-separated IDs to a list
        services = Services.objects.filter(service_id__in=service_ids)
        
        # Prepare service details
        service_details = []
        for service in services:
            service_details.append({
                'name': service.service_name,
                'price': service.price,
            })
        
        # Prepare payment details with fallback for missing fields
        payment_data = {
            'amount': payment.amount,
            'cgst': payment.cgst if hasattr(payment, 'cgst') and payment.cgst is not None else 0.00,  # Check if cgst exists
            'sgst': payment.sgst if hasattr(payment, 'sgst') and payment.sgst is not None else 0.00,  # Check if sgst exists
            'grand_total': payment.grand_total if hasattr(payment, 'grand_total') and payment.grand_total is not None else 0.00,  # Check if grand_total exists
            'coupon_code': payment.coupon_code,
            'coupon_amount': payment.coupon_amount,
            'payment_mode': payment.payment_mode if hasattr(payment, 'payment_mode') and payment.payment_mode else 'Cash',  # Default to 'Cash' if payment_mode is missing
            'payment_status': payment.payment_status,
        }
        
        # Prepare invoice data
        invoice_data = {
            'user': {
                'name': user.name,
                'phone': user.phone,
                'address': user.address,
            },
            'appointment': {
                'date': appointment.appointment_date,
                'time': appointment.appointment_time,
            },
            'payment': payment_data,
            'services': service_details,
        }
        
        return JsonResponse({'status': 'success', 'invoice': invoice_data}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)





#Invoice pdf
def generate_invoice_pdf(request):
    try:
        # Get appointment_id from query parameters
        appointment_id = request.GET.get('appointment_id')
        if not appointment_id:
            return HttpResponse("appointment_id is required", status=400)
        
        # Fetch appointment details
        appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
        user = get_object_or_404(User, user_id=appointment.user.user_id)
        payment = get_object_or_404(Payment, appointment=appointment)
        
        # Get service details
        service_ids = map(int, appointment.service_id_new.split(','))
        services = Services.objects.filter(service_id__in=service_ids)
        
        # Prepare service data for the template
        service_details = []
        for service in services:
            service_details.append({
                'name': service.service_name,
                'price': service.price,
            })
        
        # Prepare invoice data for rendering
        invoice_data = {
            'user': {
                'name': user.name,
                'phone': user.phone,
                'address': user.address,
            },
            'appointment': {
                'date': appointment.appointment_date,
                'time': appointment.appointment_time,
            },
            'payment': {
                'amount': payment.amount,
                'cgst': payment.cgst,
                'sgst': payment.sgst,
                'grand_total': payment.grand_total,
                'coupon_code': payment.coupon_code,
                'coupon_amount': payment.coupon_amount,
                'payment_mode': payment.payment_mode,
                'payment_status': payment.payment_status,
            },
            'services': service_details,
        }
        
        # Define HTML content
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Invoice</title>
            <style>
                body { font-family: Arial, sans-serif; }
                .header { text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; }
                .section { margin-bottom: 20px; }
                .details, .services { width: 100%; border-collapse: collapse; }
                .details td, .services th, .services td { border: 1px solid #ddd; padding: 8px; }
                .services th { text-align: left; background-color: #f2f2f2; }
                .totals { text-align: right; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="header">Invoice</div>

            <div class="section">
                <strong>Invoice to:</strong><br>
                {{ invoice.user.name }} | {{ invoice.user.phone }}<br>
                {{ invoice.user.address }}
            </div>

            <div class="section">
                <strong>Payment Details:</strong><br>
                Total Due: Rs. {{ invoice.payment.grand_total }}<br>
                Payment Mode: {{ invoice.payment.payment_mode }}<br>
                Payment Status: {{ invoice.payment.payment_status }}<br>
                Coupon: {{ invoice.payment.coupon_code|default:"NIL" }}
            </div>

            <table class="services">
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Charges</th>
                    </tr>
                </thead>
                <tbody>
                    {% for service in invoice.services %}
                    <tr>
                        <td>{{ service.name }}</td>
                        <td>Rs. {{ service.price }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>

            <div class="totals">
                <p>SGST Tax: Rs. {{ invoice.payment.sgst }}</p>
                <p>CGST Tax: Rs. {{ invoice.payment.cgst }}</p>
                <p><strong>Total: Rs. {{ invoice.payment.grand_total }}</strong></p>
            </div>
        </body>
        </html>
        """

        # Render the template using Django's Template system
        template = Template(html_content)
        context = Context({'invoice': invoice_data})
        html = template.render(context)

        # Generate the PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            response.write(result.getvalue())
            return response
        else:
            return HttpResponse("Error generating PDF", status=500)

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=400)


#Wallet Transaction
class ProviderTransactionListView(APIView):
    def get(self, request, *args, **kwargs):
        provider_id = request.query_params.get('provider_id', None)
        
        # Check if provider_id is provided
        if not provider_id:
            return Response(
                {"error": "provider_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter transactions by the provided provider_id
        transactions = ProviderTransactions.objects.filter(provider_id=provider_id)
        
        serializer = ProviderTransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#Review Approval
class ReviewApprovalAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ReviewStatusSerializer(data=request.data)
        
        if serializer.is_valid():
            review_id = serializer.validated_data.get('review_id')  
            status = serializer.validated_data.get('status')  
            
            if status is not None:  
                try:
                    # Get the review object
                    review = Review.objects.get(review_id=review_id)
                    
                    # Update the review status
                    review.status = status
                    review.save()
                    
                    return Response({"status":"success","message": "Review status updated successfully."}, status=http_status.HTTP_200_OK)
                except Review.DoesNotExist:
                    return Response({"error": "Review not found."}, status=http_status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Invalid status value."}, status=http_status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)

#Add Wallet 
class AddWalletTransactionView(APIView):
    def post(self, request, *args, **kwargs):
        provider_id = request.data.get('provider_id')
        amount = request.data.get('amount')

        # Validate provider_id and amount
        if not provider_id or not amount:
            return Response(
                {"status": "error", "message": "provider_id and amount are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if amount is greater than or equal to 2000
        if float(amount) < 2000:
            return Response(
                {"status": "error", "message": "Minimum recharge amount is 2000."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Default values
        current_date = datetime.now().date()
        current_time = datetime.now().time()
        transaction_id = "OCB3948236"
        transaction_type = "Purchase"
        payment_type = "Online"

        # Create a new transaction
        transaction = ProviderTransactions.objects.create(
            provider_id=provider_id,
            date=current_date,
            amount=amount,
            type=transaction_type,
            payment_type=payment_type,
            transaction_id=transaction_id,
            total_amount=amount  # Assuming the amount is equal to total credits
        )

        # Serialize the transaction
        serializer = ProviderTransactionSerializer(transaction)

        # Return the response with status and message
        return Response(
            {
                "status": "success",
                "message": "Transaction added successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


#Wallet credits
class CreditsView(APIView):
    def get(self, request):
        provider_id = request.query_params.get('provider_id')
        if not provider_id:
            return Response({'error': 'provider_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            provider = ServiceProvider.objects.get(provider_id=provider_id)

            # Total credits calculation (only successful transactions)
            total_credits = (
                ProviderTransactions.objects.filter(provider=provider, status="Success")
                .aggregate(Sum('total_amount'))['total_amount__sum']
            ) or Decimal(0)  # Ensure it's a Decimal

            available_credits = Decimal(provider.available_credits)
            used_credits = Decimal(0)

            # Start a database transaction to ensure atomicity
            with transaction.atomic():
                # Get all appointments with status 3
                appointments_with_status_3 = Appointment.objects.filter(
                    provider=provider,
                    status__status_id=3
                )

                total_grand_total = Decimal(0)
                for appointment in appointments_with_status_3:
                    payment = Payment.objects.filter(appointment=appointment).first()
                    if payment and payment.grand_total is not None:
                        total_grand_total += Decimal(payment.grand_total)

                # Calculate used_credits as 30% of total grand_total
                used_credits = round(total_grand_total * Decimal(0.30))

                # Calculate available credits
                available_credits = total_credits - used_credits

                # Update provider's available credits
                provider.available_credits = available_credits
                provider.save()

            # Prepare response
            data = {
                'status': 'success',
                'message': 'Credits successfully updated',
                'provider_id': provider_id,
                'total_credits': int(total_credits),
                'available_credits': int(available_credits),
                'used_credits': int(used_credits),
            }

            return Response(data, status=status.HTTP_200_OK)

        except ServiceProvider.DoesNotExist:
            return Response({'error': 'Provider not found'}, status=status.HTTP_404_NOT_FOUND)

#Package Management
class PackageDetailsView(APIView):
    def get(self, request):
        provider_id = request.query_params.get('provider_id')
        branch_id = request.query_params.get('branch_id')  # Optional parameter
        search_query = request.query_params.get('search', '')  # Optional search parameter

        if not provider_id:
            return Response({"status": "error", "message": "provider_id is required"}, status=400)

        # Base filter with provider_id and is_deleted = False
        filters = {"provider_id": provider_id, "is_deleted": False}

        # Add branch_id filter if provided
        if branch_id:
            filters["branch_id"] = branch_id

        # Filter services based on the constructed filters
        services = Services.objects.filter(**filters)

        # Apply search filter if search_query is provided
        if search_query:
            services = services.filter(
                Q(service_name__icontains=search_query) |  
                Q(package_services__icontains=search_query)
            )

        # Order by descending service_id (recently added first)
        services = services.order_by('-service_id')

        # Select required fields
        services = services.values(
            'service_id', 'service_name', 'price', 'package_services', 'status', 'is_deleted'
        )

        # Apply pagination
        paginator = CustomPagination()
        paginated_services = paginator.paginate_queryset(services, request)

        # Construct the response
        return paginator.get_paginated_response({
            "status": "success",
            "message": "Package details fetched successfully",
            "data": paginated_services
        })

#Add Packages
class AddPackageServiceView(APIView):
    def post(self, request):
        serializer = AddPackageServiceSerializer(data=request.data)
        if serializer.is_valid():
            # Save the serializer and get the created/updated instance
            instance = serializer.save()
            return Response({
                "status": "success",
                "message": "Package service added successfully",
                "data": {
                    "package_id": instance.service_id,  # Return service_id as package_id
                    **serializer.to_representation(instance)  # Include other serialized data
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Invalid data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


#Edit Packages
class EditPackageServiceView(APIView):
    def put(self, request):
        # Extract service_id from the request data
        service_id = request.data.get("service_id")
        if not service_id:
            return Response({
                "status": "error",
                "message": "Service ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the package service by service_id
            package_service = Services.objects.get(service_id=service_id)
        except Services.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Package service not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Use the serializer with the existing instance
        serializer = AddPackageServiceSerializer(
            package_service,
            data=request.data,
            partial=True  # Allow partial updates
        )
        if serializer.is_valid():
            # After saving, update the package_services_ids field
            updated_instance = serializer.save()

            # Get the selected_service_ids from the request data and convert to comma-separated list
            selected_service_ids = request.data.get('selected_service_ids')
            if selected_service_ids:
                selected_service_ids_list = selected_service_ids.split(',')
                package_services_ids = ', '.join(map(str, selected_service_ids_list))

                # Save the package_services_ids field
                updated_instance.package_services_ids = package_services_ids
                updated_instance.save()

            return Response({
                "status": "success",
                "message": "Package service updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "Invalid data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



#Delete Packages
class DeletePackageServiceView(APIView):
    def delete(self, request):
        # Extract service_id from the request data
        service_id = request.data.get("service_id")
        if not service_id:
            return Response({
                "status": "error",
                "message": "Service ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the package service by service_id
            package_service = Services.objects.get(service_id=service_id)
        except Services.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Package service not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Perform a soft delete by setting is_deleted to True
        package_service.is_deleted = True
        package_service.save()

        return Response({
            "status": "success",
            "message": "Package service soft deleted successfully"
        }, status=status.HTTP_200_OK)



#Active Packages
class ActivePackagesByProviderView(APIView):
    def get(self, request):
        # Retrieve provider_id and optional branch_id from query parameters
        provider_id = request.query_params.get('provider_id', None)
        branch_id = request.query_params.get('branch_id', None)

        if not provider_id:
            return Response({
                "status": "error",
                "message": "provider_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Base query filter
        filters = {
            "provider_id": provider_id,
            "is_deleted": False
        }

        # Apply branch_id filter only if provided
        if branch_id:
            filters["branch_id"] = branch_id

        # Filter the active packages
        active_packages = Services.objects.filter(**filters)

        if not active_packages.exists():
            return Response({
                "status": "error",
                "message": "No active packages found for the given provider"
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the active packages
        serializer = PackagesSerializer(active_packages, many=True)

        return Response({
            "status": "success",
            "message": "Active packages retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

#Update Active Packages   
class UpdateActivePackagesView(APIView):
    def put(self, request):
        # Get package data from request body
        packages = request.data.get("packages", [])

        # Handle case where packages are sent as a string
        if isinstance(packages, str):
            try:
                packages = json.loads(packages)  # Parse the string into a list of objects
            except json.JSONDecodeError:
                return Response({
                    "status": "error",
                    "message": "Invalid packages format. Must be a JSON array of objects."
                }, status=status.HTTP_400_BAD_REQUEST)

        # Validate that packages are in the correct structure
        if not isinstance(packages, list):
            return Response({
                "status": "error",
                "message": "packages must be a list of objects"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Iterate through the packages and update
        updated_count = 0
        for package in packages:
            package_id = package.get("package_id")
            if not package_id:
                continue

            # Fetch the service by package_id
            try:
                service = Services.objects.get(service_id=package_id)
            except Services.DoesNotExist:
                continue

            # Update fields if they are provided
            if "price" in package:
                service.price = package["price"]
            if "is_deleted" in package:
                service.is_deleted = package["is_deleted"]

            # Save the updated service
            service.save()
            updated_count += 1

        if updated_count == 0:
            return Response({
                "status": "error",
                "message": "No valid packages were updated"
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "status": "success",
            "message": "Packages updated successfully"
        }, status=status.HTTP_200_OK)



#Get provider List   
class ServiceProviderListView(APIView):
    pagination_class = CustomPagination

    def get(self, request):
        provider_status = request.query_params.get('status', None)  # Get status from query params
        search_query = request.query_params.get('search', None)  # Get search term from query params

        if not provider_status:
            return Response({
                "status": "failure",
                "message": "Status is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch providers based on status and exclude deleted providers
        providers = ServiceProvider.objects.filter(
            status=provider_status, 
            is_deleted=False  # Only fetch non-deleted providers
        ).order_by('-provider_id')  # Changed to descending order

        # Apply search filter if search query exists
        if search_query:
            providers = providers.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(owner_name__icontains=search_query) |
                Q(branch__location__city__icontains=search_query)  # Ensure branch relation is correct
            ).distinct()

        # Apply pagination
        paginator = CustomPagination()
        paginated_providers = paginator.paginate_queryset(providers, request)

        # Prepare response data
        response_data = []
        for provider in paginated_providers:
            branch = getattr(provider, 'branch', None)  # Safely get the branch
            location = getattr(branch, 'location', None) if branch else None
            response_data.append({
                'salon_id': provider.provider_id,
                'salon_name': provider.name,
                'email': provider.email,
                'mobile': provider.phone,
                'owner_name': provider.owner_name,
                'location': getattr(location, 'city', None) if location else None,
            })

        return paginator.get_paginated_response({
            "status": "success",
            "message": "Provider list retrieved successfully.",
            "data": response_data,
        })

        
#Super Admin Login
class SuperAdminLoginViewSet(viewsets.ModelViewSet):
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer

    def create(self, request, *args, **kwargs):
        phone = request.data.get('phone')

        if not phone:
            return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not AdminUser.objects.filter(phone_number=phone).exists():
            return Response({'status': 'failure', 'message': 'Superadmin not registered'}, status=status.HTTP_400_BAD_REQUEST)

        admin_entry = AdminUser.objects.get(phone_number=phone)

        # Dynamically generate OTP
        # otp = ''.join(random.choices(string.digits, k=4))
        
        # Set static OTP for testing
        otp = "1234"

        admin_entry.otp = otp
        admin_entry.otp_created_at = timezone.now()
        admin_entry.save()

        return Response({
            'status': 'success',
            'otp': otp,  # Return OTP for testing purposes (in a real app, you'd send this via SMS)
            'message': 'OTP generated and sent successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        otp = request.data.get('otp')
    
        if not phone or not otp:
            return Response({'status': 'failure', 'message': 'Phone and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            admin_entry = AdminUser.objects.get(phone_number=phone)
        except AdminUser.DoesNotExist:
            return Response({'status': 'failure', 'message': 'Superadmin not found'}, status=status.HTTP_404_NOT_FOUND)
    
        # Convert both OTPs to strings and then strip
        stored_otp = str(admin_entry.otp).strip()
        received_otp = str(otp).strip()
    
        if stored_otp == received_otp:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
    
            admin_entry.token = token
            admin_entry.save()
    
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'token': admin_entry.token,
                'admin_id': admin_entry.id
            }, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'failure', 'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

#Accept Provider        
class UpdateServiceProviderStatus(APIView):
    def post(self, request):
        # Extract provider_id and new status from the request body
        provider_id = request.data.get('provider_id')
        new_status = request.data.get('status')

        if not provider_id:
            return Response(
                {"status": "failure", "message": "Provider ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not new_status or new_status not in ['Active', 'Inactive']:
            return Response(
                {
                    "status": "failure",
                    "message": "Invalid status. Allowed values are 'Active' or 'Inactive'.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch the ServiceProvider instance by provider_id
        service_provider = get_object_or_404(ServiceProvider, provider_id=provider_id)

        # Remove restriction on moving from Pending to Inactive
        if service_provider.status == new_status:
            return Response(
                {
                    "status": "failure",
                    "message": f"Service Provider is already {new_status}.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update the status
        service_provider.status = new_status
        service_provider.save()

        return Response(
            {
                "status": "success",
                "message": f"Service Provider status updated to {new_status}.",
                "data": {
                    "provider_id": service_provider.provider_id,
                    "name": service_provider.name,
                    "status": service_provider.status,
                },
            },
            status=status.HTTP_200_OK,
        )


class ProviderDetailsView(APIView):
    def get(self, request, format=None):
        provider_id = request.query_params.get('provider_id')  # Fetch provider_id from query parameters
        
        if not provider_id:
            return Response(
                {"status": "error", "message": "Provider ID is required.", "data": {}}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            provider = ServiceProvider.objects.get(provider_id=provider_id)
        except ServiceProvider.DoesNotExist:
            return Response(
                {"status": "error", "message": "Provider not found.", "data": {}}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProviderDetailsSerializer(provider)
        return Response(
            {
                "status": "success",
                "message": "Provider details fetched successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

#Update General Info
class UpdateProviderDetails(APIView):
    def put(self, request, format=None):
        request_data = request.data.copy()

        # Get provider_id from the form data
        provider_id = request_data.get('provider_id')

        if not provider_id:
            return Response({"detail": "Provider ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        provider = get_object_or_404(ServiceProvider, provider_id=provider_id)

        # Handle branch update
        branch_name = request_data.get('branch')
        if branch_name:
            branch = Branches.objects.filter(location__city=branch_name, is_deleted=False).first()
            if branch:
                provider.branch = branch  # Assign the branch object
            else:
                return Response({"detail": "Branch not found."}, status=status.HTTP_404_NOT_FOUND)

        # Handle address update
        address_value = request_data.get('address')
        if address_value:
            branch = Branches.objects.filter(location__address_line1=address_value, is_deleted=False).first()
            if branch:
                provider.address = branch.location  # Assign the location object
            else:
                return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize and validate the data
        serializer = ProviderDetailsSerializer(provider, data=request_data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # Update bank details
            bank_details_data = request_data.get('bank_details', [])
            if bank_details_data:
                for bank_data in bank_details_data:
                    bank_id = bank_data.get('bank_id')
                    if bank_id:
                        bank = ProviderBankDetails.objects.filter(id=bank_id).first()
                        if bank:
                            for key, value in bank_data.items():
                                setattr(bank, key, value)
                            bank.save()
                        else:
                            new_bank = ProviderBankDetails(**bank_data, provider=provider)
                            new_bank.save()
                    else:
                        new_bank = ProviderBankDetails(**bank_data, provider=provider)
                        new_bank.save()

            # Update tax details
            tax_details_data = request_data.get('tax_details', [])
            if tax_details_data:
                for tax_data in tax_details_data:
                    tax_id = tax_data.get('tax_id')
                    if tax_id:
                        tax = ProviderTaxRegistration.objects.filter(id=tax_id).first()
                        if tax:
                            for key, value in tax_data.items():
                                setattr(tax, key, value)
                            tax.save()
                        else:
                            new_tax = ProviderTaxRegistration(**tax_data, provider=provider)
                            new_tax.save()
                    else:
                        new_tax = ProviderTaxRegistration(**tax_data, provider=provider)
                        new_tax.save()

            return Response({
                "status": "success",
                "message": "Provider details updated successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "Failed to update provider details.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

#Stylist 
class StylistListView(APIView):
    def get(self, request):
        provider_id = request.query_params.get('provider_id')
        
        if not provider_id:
            return Response(
                {"status": "error", "message": "provider_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch stylists with role_id=5 and the given provider_id
        stylists = Staff.objects.filter(provider_id=provider_id, role_id=5, is_deleted=False)

        if not stylists.exists():
            return Response(
                {"status": "error", "message": "No stylists found for this provider"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StaffSerializer(stylists, many=True)

        return Response(
            {"status": "success", "message": "Stylists retrieved successfully", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
def toggle_service_status(request):
    """
    API to toggle service status (Active/Inactive)
    """
    service_id = request.data.get('service_id')
    new_status = request.data.get('status')  # Expecting "Active" or "Inactive"

    if not service_id or new_status not in ["Active", "Inactive"]:
        return Response({"status": "failure","message": "service_id and status is required"}, status=400)

    service = get_object_or_404(Services, service_id=service_id)

    # Update status
    service.status = new_status
    service.save()

    return Response({"status": "success","message": "Service status updated successfully"}, status=200)


@api_view(['POST'])
def update_service_status(request):
    # Get branch_id and service_status from query parameters
    branch_id = request.data.get('branch_id')
    service_status = request.data.get('service_status')

    if not branch_id or not service_status:
        return Response({"status":"failure","message": "Both branch_id and service_status are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        service_status = int(service_status)
    except ValueError:
        return Response({"error": "service_status must be an integer (0 or 1)."}, status=status.HTTP_400_BAD_REQUEST)

    if service_status not in [0, 1]:
        return Response({"error": "Invalid service_status. Please use 0 (offline) or 1 (online)."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        branch = Branches.objects.get(branch_id=branch_id)
    except Branches.DoesNotExist:
        return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

    # Update the branch with the new service status
    branch.service_status = service_status
    branch.save()

    return Response({"status":"success","message": "Service status updated successfully"}, status=status.HTTP_200_OK)

#Update Payment Status
class UpdatePaymentStatus(APIView):
    def post(self, request):
        appointment_id = request.data.get("appointment_id")
        payment_status = request.data.get("payment_status")

        if not appointment_id or not payment_status:
            return Response({"status":"failure","message": "appointment_id and payment_status are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the appointment exists
        appointment = get_object_or_404(Appointment, appointment_id=appointment_id)

        # Get the related payment
        payment = get_object_or_404(Payment, appointment=appointment)

        # Validate payment status
        valid_statuses = ["Paid", "Partly Paid", "Not Paid"]
        if payment_status not in valid_statuses:
            return Response({"status":"failure","message": "Invalid payment status"}, status=status.HTTP_400_BAD_REQUEST)

        # Update and save
        payment.payment_status = payment_status
        payment.save()

        return Response({"status":"success","message": "Payment status updated successfully"}, status=status.HTTP_200_OK)

#Cancel Appointment
class CancelAppointmentView(APIView):

    def post(self, request):
        appointment_id = request.data.get("appointment_id")  # Get appointment_id from JSON
        if not appointment_id:
            return Response({"status": "error", "message": "appointment_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        appointment = get_object_or_404(Appointment, appointment_id=appointment_id)

        # Check if the status with ID 4 exists
        cancelled_status = get_object_or_404(Status, status_id=4)

        # Update appointment status
        appointment.status = cancelled_status
        appointment.save()

        return Response({
            "status": "success",
            "message": "Appointment has been cancelled successfully."
        }, status=status.HTTP_200_OK)


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


#Get provider cities
class ProviderBranchesCityView(APIView):
    def get(self, request, format=None):
        provider_id = request.GET.get('provider_id')
        
        if not provider_id:
            return Response({
                'status': 'error',
                'message': 'provider_id is required ',
                'data': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch all branch details
        branches = Branches.objects.filter(provider_id=provider_id, is_deleted=False).values(
            'branch_id', 
            'branch_name', 
            'location__location_id',
            'location__city'
        )

        if not branches:
            return Response({
                'status': 'error',
                'message': 'No branches found for the provided provider.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)
        
        unique_cities = set()
        filtered_branches = []

        for branch in branches:
            city_name = branch['location__city']
            
            if len(city_name) < 5:  # Ignore cities with less than 5 characters
                continue

            city_key = city_name[:5].lower()  # Extract first 5 letters (case insensitive)
            
            if city_key not in unique_cities:
                unique_cities.add(city_key)
                filtered_branches.append({
                    'branch_id': branch['branch_id'],
                    'branch_name': branch['branch_name'],
                    'location_id': branch['location__location_id'],
                    'city': city_name
                })

        return Response({
            'status': 'success',
            'message': 'Branches cities retrieved successfully.',
            'data': filtered_branches
        }, status=status.HTTP_200_OK)


# Razorpay Credentials
RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET

# Store successful payments temporarily before adding to wallet
# Store successful payments temporarily before adding to wallet
verified_payments = {}

class CreateOrderView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            amount = request.data.get("amount")
            currency = request.data.get("currency", "INR")
            receipt = request.data.get("receipt")
            provider_id = request.data.get("provider_id")  # Store provider_id

            if not amount or not receipt:
                return Response({
                    "status": "failure",
                    "message": "Missing required fields",
                    "missing_fields": [field for field in ["amount", "receipt"] if not request.data.get(field)]
                }, status=status.HTTP_400_BAD_REQUEST)

            # Initialize Razorpay client
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
            order_data = {
                "amount": int(float(amount) * 100),  # Convert to paisa
                "currency": currency,
                "receipt": receipt,
                "payment_capture": 1  # Auto capture payment
            }

            order = client.order.create(order_data)

            # ✅ Store provider_id temporarily using order_id as key
            verified_payments[order["id"]] = provider_id

            return Response({
                "status": "success",
                "message": "Order created successfully",
                "order": order
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Verify Payment
class VerifyPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            razorpay_order_id = request.data.get("razorpay_order_id")
            razorpay_payment_id = request.data.get("razorpay_payment_id")
            razorpay_signature = request.data.get("razorpay_signature")
            provider_id = request.data.get("provider_id")  # Capture provider ID

            if not razorpay_order_id:
                return Response({"status": "failure", "message": "Missing order ID"}, status=status.HTTP_400_BAD_REQUEST)

            # Initialize Razorpay client
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            }

            try:
                # Verify payment signature
                client.utility.verify_payment_signature(params_dict)

                # Fetch order details
                order = client.order.fetch(razorpay_order_id)
                amount = Decimal(order["amount"]) / Decimal(100)  # Convert back to currency format

                # ✅ Calculate CGST and SGST (9% each)
                cgst = (amount * Decimal(9)) / Decimal(100)  # 9% CGST
                sgst = (amount * Decimal(9)) / Decimal(100)  # 9% SGST
                total_amount = amount + cgst + sgst  # Grand Total

                # ✅ Store successful payment including CGST & SGST
                transaction = ProviderTransactions.objects.create(
                    provider_id=provider_id,
                    date=now().date(),
                    amount=amount,
                    type="Purchase",
                    payment_type="Online",
                    transaction_id=razorpay_payment_id,
                    order_id=razorpay_order_id,
                    total_amount=total_amount,
                    cgst=cgst,  # Store CGST
                    sgst=sgst,  # Store SGST
                    status="Success"
                )

                return Response({
                    "status": "success",
                    "message": "Payment verified successfully.",
                    "orderID": razorpay_order_id,
                    "paymentID": razorpay_payment_id,
                    "cgst": float(cgst),
                    "sgst": float(sgst),
                    "total_amount": float(total_amount)
                }, status=status.HTTP_200_OK)

            except razorpay.errors.SignatureVerificationError:
                # Store failed payment if verification fails
                ProviderTransactions.objects.create(
                    provider_id=provider_id,
                    date=now().date(),
                    amount=0,  # Failed payments have no valid amount
                    type="Purchase",
                    payment_type="Online",
                    transaction_id=None,
                    order_id=razorpay_order_id,
                    total_amount=0,
                    status="Failed"
                )

                return Response({"status": "failure", "message": "Signature verification failed"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Cancel Payment 
class CancelPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            order_id = request.data.get("order_id")  # Razorpay Order ID
            provider_id = request.data.get("provider_id")  # Optional provider ID

            if not order_id:
                return Response({
                    "status": "failure",
                    "message": "Missing order_id"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if the transaction exists
            transaction = ProviderTransactions.objects.filter(order_id=order_id).first()

            if not transaction:
                # Store failed order in the DB if it wasn't found
                ProviderTransactions.objects.create(
                    provider_id=provider_id,
                    date=now().date(),
                    amount=0,
                    type="Purchase",
                    payment_type="Online",
                    transaction_id=None,
                    order_id=order_id,
                    total_amount=0,
                    status="Failed"
                )

                return Response({
                    "status": "failure",
                    "message": "Transaction not found. Marked as failed."
                }, status=status.HTTP_404_NOT_FOUND)

            if transaction.status == "Success":
                return Response({
                    "status": "failure",
                    "message": "Cannot cancel a successful payment"
                }, status=status.HTTP_400_BAD_REQUEST)

            # If payment was initiated but not completed, mark as "Failed"
            transaction.status = "Failed"
            transaction.save()

            return Response({
                "status": "success",
                "message": "Payment canceled successfully",
                "order_id": order_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Create Wallet
class CreateWalletTransactionView(APIView):
    def post(self, request, *args, **kwargs):
        provider_id = request.data.get('provider_id')
        amount = request.data.get('amount')
        razorpay_payment_id = request.data.get("transaction_id")  # Use payment_id instead of order_id
        razorpay_order_id = request.data.get("order_id")  # Added order_id

        if not provider_id or not amount or not razorpay_payment_id or not razorpay_order_id:
            return Response(
                {"status": "error", "message": "provider_id, amount, transaction_id (razorpay_payment_id), and order_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Check if the payment ID exists in verified payments
        if razorpay_payment_id not in verified_payments.values():
            return Response(
                {"status": "error", "message": "Payment verification not found. Please verify payment first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Fetch payment details from Razorpay to confirm success
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        payment = client.payment.fetch(razorpay_payment_id)

        if payment["status"] != "captured":
            return Response({"status": "error", "message": "Payment not successful."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Update only if status is 'Success'
        try:
            transaction = ProviderTransactions.objects.get(order_id=razorpay_order_id, transaction_id="")

            # ✅ Update transaction with payment ID & mark as Success
            transaction.transaction_id = razorpay_payment_id
            transaction.status = "Success"
            transaction.save()

            # ✅ Add credits to provider's wallet only if success
            provider = ServiceProvider.objects.get(id=provider_id)
            provider.wallet_balance += Decimal(amount)
            provider.save()

            # ✅ Serialize response
            serializer = ProviderTransactionSerializer(transaction)

            return Response(
                {
                    "status": "success",
                    "message": "Transaction successful. Credits added to wallet.",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        except ProviderTransactions.DoesNotExist:
            return Response({"status": "error", "message": "Transaction not found or already updated."}, status=status.HTTP_404_NOT_FOUND)

        except ServiceProvider.DoesNotExist:
            return Response({"status": "error", "message": "Provider not found."}, status=status.HTTP_404_NOT_FOUND)

#Appointment Edit 
class EditAppointmentView(APIView):
    def put(self, request, *args, **kwargs):
        appointment_id = request.data.get('appointment_id')
        selected_services = request.data.get('services')

        if not appointment_id:
            return Response({
                "status": "failure",
                "message": "appointment_id is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            appointment = Appointment.objects.get(pk=appointment_id)
        except Appointment.DoesNotExist:
            return Response({
                "status": "failure",
                "message": "Appointment not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Convert service IDs to a list of integers if given as a string
        if isinstance(selected_services, str):
            selected_services = [int(service_id) for service_id in selected_services.split(',') if service_id.isdigit()]

        if not selected_services:
            return Response({
                "status": "failure",
                "message": "Invalid service IDs provided."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch service details based on selected service IDs
        services = Services.objects.filter(service_id__in=selected_services)
        if not services.exists():
            return Response({
                "status": "failure",
                "message": "No valid services found for the given IDs."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price
        total_price = sum(float(service.price) for service in services if service.price)

        # Convert list to comma-separated string for storing in `service_id_new`
        appointment.service_id_new = ",".join(map(str, selected_services))
        appointment.price = total_price
        appointment.save()

        return Response({
            "status": "success",
            "message": "Appointment updated successfully.",
            "data": {
                "appointment_id": appointment_id,
                "selected_services": selected_services,
                "total_price": total_price
            }
        }, status=status.HTTP_200_OK)



#Super Admin Booking List   
class SuperAdminBookingListAPIView(APIView):
    def get(self, request):
        sort_order = request.query_params.get("sort_order", "desc")

        try:
            now = datetime.now()
            order_by_field = "-appointment_id" if sort_order == "desc" else "appointment_id"

            bookings = (
            Appointment.objects.filter(
                status_id=0,
                appointment_date__gte=now.date(),
            )
            .exclude(branch__isnull=True)
            .select_related("branch", "provider")  # Optimize DB queries
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

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# Category CRUD Operation
@api_view(['GET'])
def category_list(request):
    """Get all categories that are not deleted with optional search and pagination"""
    
    search_query = request.query_params.get('search', '')  # Get search keyword

    categories = Category.objects.filter(is_deleted=False).order_by('-category_id')  # Descending order

    if search_query:
        categories = categories.filter(category_name__icontains=search_query)  # Case-insensitive search

    paginator = CustomPagination()
    paginated_categories = paginator.paginate_queryset(categories, request)

    serializer = CategorySerializer(paginated_categories, many=True)

    return paginator.get_paginated_response({
        "status": "success",
        "message": "Categories fetched successfully",
        "data": serializer.data
    })



@api_view(['POST'])
def add_category(request):
    """Add a new category"""
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Category added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        "status": "failure",
        "message": "Invalid data",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
def edit_category(request):
    """Edit an existing category using category_id from raw data"""

    category_id = request.data.get('category_id')  # Get from request body

    if not category_id:
        return Response({
            "status": "failure",
            "message": "category_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        category = Category.objects.get(category_id=category_id, is_deleted=False)
    except Category.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Category not found"
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = CategorySerializer(category, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Category updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        "status": "failure",
        "message": "Invalid data",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_category(request):
    """Soft delete a category using query param category_id"""
    category_id = request.query_params.get('category_id')  # Get from query params

    if not category_id:
        return Response({
            "status": "failure",
            "message": "category_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        category = Category.objects.get(category_id=category_id, is_deleted=False)
        category.is_deleted = True  # Soft delete
        category.save()
        
        return Response({
            "status": "success",
            "message": "Category deleted successfully"
        }, status=status.HTTP_200_OK)
    
    except Category.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Category not found"
        }, status=status.HTTP_404_NOT_FOUND)

#Subcategory CRUD Operation
@api_view(['GET'])
def get_subcategories(request):
    """Fetch all subcategories grouped by category with optional search, pagination, and descending order"""
    
    search_query = request.query_params.get('search', '')  # Get search keyword

    subcategories = Subcategory.objects.filter(is_deleted=False).select_related('category').order_by('-subcategory_id')  # Descending order

    if search_query:
        subcategories = subcategories.filter(subcategory_name__icontains=search_query)  # Case-insensitive search

    paginator = CustomPagination()
    paginated_subcategories = paginator.paginate_queryset(subcategories, request)

    category_dict = defaultdict(lambda: {"category_id": None, "category_name": None, "subcategories": []})

    for sub in paginated_subcategories:
        category_id = sub.category.category_id
        category_name = sub.category.category_name

        if category_dict[category_id]["category_id"] is None:
            category_dict[category_id]["category_id"] = category_id
            category_dict[category_id]["category_name"] = category_name

        category_dict[category_id]["subcategories"].append({
            "subcategory_id": sub.subcategory_id,
            "subcategory_name": sub.subcategory_name,
            "status": sub.status,
            "is_deleted": sub.is_deleted
        })

    response_data = list(category_dict.values())

    return paginator.get_paginated_response({
        "status": "success",
        "message": "Subcategories fetched successfully",
        "data": response_data
    })


# 2️⃣ Add a New Subcategory
@api_view(['POST'])
def add_subcategory(request):
    """Add a new subcategory"""
    serializer = SubcategoriesSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Subcategory added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "status": "failure",
        "message": "Validation failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# 3️⃣ Edit a Subcategory
@api_view(['PUT'])
def edit_subcategory(request):
    """Edit an existing subcategory using subcategory_id from raw data"""
    
    subcategory_id = request.data.get('subcategory_id')  # Get from request body
    category_id = request.data.get('category_id')  # New category_id from request body

    if not subcategory_id:
        return Response({
            "status": "failure",
            "message": "subcategory_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        subcategory = Subcategory.objects.get(subcategory_id=subcategory_id, is_deleted=False)

        # Check if category_id exists before updating
        if category_id:
            try:
                category = Category.objects.get(category_id=category_id, is_deleted=False)
                subcategory.category = category  # Assign new category
            except Category.DoesNotExist:
                return Response({
                    "status": "failure",
                    "message": "Invalid category_id. Category not found"
                }, status=status.HTTP_400_BAD_REQUEST)

        # Serialize and update the subcategory
        serializer = SubcategorySerializer(subcategory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Subcategory updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "failure",
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Subcategory.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Subcategory not found"
        }, status=status.HTTP_404_NOT_FOUND)


# 4️⃣ Soft Delete a Subcategory
@api_view(['DELETE'])
def delete_subcategory(request):
    """Soft delete a subcategory using query param subcategory_id"""
    subcategory_id = request.query_params.get('subcategory_id')  # Get from query params

    if not subcategory_id:
        return Response({
            "status": "failure",
            "message": "subcategory_id is required in query params"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        subcategory = Subcategory.objects.get(subcategory_id=subcategory_id, is_deleted=False)
        subcategory.is_deleted = True  # Soft delete
        subcategory.save()

        return Response({
            "status": "success",
            "message": "Subcategory deleted successfully"
        }, status=status.HTTP_200_OK)

    except Subcategory.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Subcategory not found"
        }, status=status.HTTP_404_NOT_FOUND)


#Services CRUD Operation
@api_view(['GET'])
def get_services(request):
    """Fetch all services that are not deleted, ordered by service_id, with optional search, category, subcategory filters, and pagination"""

    search_query = request.query_params.get('search', '')  # Get search keyword
    category_id = request.query_params.get('category')  # Get category filter
    subcategory_id = request.query_params.get('subcategory')  # Get subcategory filter

    services = Services.objects.filter(is_deleted=False).select_related('category', 'subcategory')

    # Apply filters if provided
    if search_query:
        services = services.filter(service_name__icontains=search_query)  # Case-insensitive search

    if category_id and category_id != '0':
        services = services.filter(category_id=category_id)

    if subcategory_id and subcategory_id != '0':
        services = services.filter(subcategory_id=subcategory_id)

    services = services.order_by('-service_id')  # Order by service_id descending

    # Apply Pagination
    paginator = CustomPagination()
    paginated_services = paginator.paginate_queryset(services, request)

    serializer = ServicesSerializer(paginated_services, many=True)

    return paginator.get_paginated_response({
        "status": "success",
        "message": "Services fetched successfully",
        "data": serializer.data
    })



@api_view(['POST'])
def add_service(request):
    """Add a new service with auto-generated SKU value"""
    serializer = ServicesSerializer(data=request.data)

    if serializer.is_valid():
        service = serializer.save()  # Save the service instance to get service_id

        # Generate SKU value using service_id (e.g., MB131 for service_id = 131)
        service.sku_value = f"MB{service.service_id}"
        service.save()  # Save the updated SKU value

        return Response({
            "status": "success",
            "message": "Service added successfully",
            "data": ServicesSerializer(service).data  # Serialize updated object
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "status": "failure",
        "message": "Validation failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def edit_service(request):
    """Edit an existing service using service_id from raw data"""

    service_id = request.data.get('service_id')  # Get from request body

    if not service_id:
        return Response({
            "status": "failure",
            "message": "service_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        service = Services.objects.get(service_id=service_id, is_deleted=False)
        serializer = ServicesSerializer(service, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Service updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "failure",
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Services.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Service not found"
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_service(request):
    """Soft delete a service using query param service_id"""
    service_id = request.query_params.get('service_id')

    if not service_id:
        return Response({
            "status": "failure",
            "message": "service_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        service = Services.objects.get(service_id=service_id, is_deleted=False)
        service.is_deleted = True  # Mark as deleted instead of deleting
        service.save()

        return Response({
            "status": "success",
            "message": "Service soft deleted successfully"
        }, status=status.HTTP_200_OK)

    except Services.DoesNotExist:
        return Response({
            "status": "failure",
            "message": "Service not found"
        }, status=status.HTTP_404_NOT_FOUND)

#All Review List
class ReviewListView(APIView, PageNumberPagination):  # Use APIView, No Router Required
    def get(self, request):
        """Fetch all reviews, attach order_id (appointment_id), related services, and search functionality"""

        search_query = request.query_params.get('search', '')  # Get search keyword

        # Fetch all reviews
        reviews = Review.objects.all().order_by('-created_at')

        # Apply search filter across multiple fields
        if search_query:
            reviews = reviews.filter(
                Q(comment__icontains=search_query) |
                Q(rating__icontains=search_query) |
                Q(user_id__in=User.objects.filter(
                    Q(name__icontains=search_query) | 
                    Q(email__icontains=search_query) | 
                    Q(phone__icontains=search_query)
                ).values_list('user_id', flat=True))
            )

        # Attach order_id (appointment_id) and services to each review
        for review in reviews:
            appointment = Appointment.objects.filter(provider_id=review.provider_id, user_id=review.user_id).first()
            if appointment:
                review.order_id = appointment.appointment_id  # Set order_id from appointment_id

                # Get services related to the appointment
                service_ids = appointment.service_id_new.split(',')  # Assuming service IDs are stored as CSV
                service_objects = Services.objects.filter(service_id__in=service_ids)

                # Convert services to array of objects
                review.service_objects = [
                    {"service_id": service.service_id, "service_name": service.service_name}
                    for service in service_objects
                ]

        # Apply pagination
        paginated_reviews = self.paginate_queryset(reviews, request, view=self)
        serializer = ReviewSerializer(paginated_reviews, many=True)

        return self.get_paginated_response({
            "status": "success",
            "message": "Reviews fetched successfully",
            "data": serializer.data
        })


#All Appointment List
class AllAppointmentsListView(APIView):
    """
    API to list appointments with optional status and search filters.
    """

    def get(self, request, *args, **kwargs):
        status_filter = request.GET.get('status')  # Optional status filter
        search_query = request.GET.get('search', '')  # Optional search query

        # Filter appointments based on optional status filter
        if status_filter:
            appointments = Appointment.objects.filter(status__status_id=status_filter)
        else:
            appointments = Appointment.objects.all()

        appointments = appointments.select_related('branch__location', 'status', 'stylist', 'user', 'provider').order_by('-appointment_id')

        # Apply search filters
        if search_query:
            matching_service_ids = Services.objects.filter(
                Q(service_name__icontains=search_query) |
                Q(price__icontains=search_query)
            ).values_list('service_id', flat=True)

            matching_service_ids = [str(service_id) for service_id in matching_service_ids]

            appointments = appointments.filter(
                Q(user__name__icontains=search_query) |
                Q(user__phone__icontains=search_query) |
                Q(stylist__name__icontains=search_query) |
                Q(status__status_name__icontains=search_query) |
                Q(branch__location__city__icontains=search_query) |
                Q(appointment_date__icontains=search_query) |
                Q(appointment_time__icontains=search_query) |
                Q(service_id_new__icontains=search_query) |
                Q(service_id_new__regex=r'(^|,)' + '|'.join(matching_service_ids) + r'(,|$)')
            )

        # Paginate the results
        paginator = CustomPagination()
        paginated_appointments = paginator.paginate_queryset(appointments, request)

        data = []
        for appointment in paginated_appointments:
            service_ids = appointment.service_id_new.split(",") if appointment.service_id_new else []
            services = Services.objects.filter(service_id__in=service_ids)
            service_details = [
                {"service_id": service.service_id, "name": service.service_name, "price": float(service.price) if service.price else 0}
                for service in services
            ]
            total_amount = sum(float(service["price"]) for service in service_details)

            # Get the correct amount: from payment if available
            payment = Payment.objects.filter(appointment=appointment).first()
            if payment and payment.grand_total is not None:
                total_amount = float(payment.grand_total)

            # Format date and time
            try:
                formatted_date = datetime.strptime(str(appointment.appointment_date), "%Y-%m-%d").strftime("%d %b %Y")
                formatted_time = datetime.strptime(str(appointment.appointment_time), "%H:%M:%S").strftime("%H:%M")
            except ValueError:
                formatted_date = str(appointment.appointment_date)
                formatted_time = str(appointment.appointment_time)

            city = appointment.branch.location.city if appointment.branch and appointment.branch.location else None
            stylist_name = appointment.stylist.name if appointment.stylist else None
            stylist_id = appointment.stylist.staff if appointment.stylist else None
            status_name = appointment.status.status_name if appointment.status else "No Status"
            status_id = appointment.status.status_id if appointment.status else None
            payment_status = payment.payment_status if payment else "Not Paid"
            provider_name = appointment.provider.name if appointment.provider else "No Provider"

            # **Fix for the `NoneType` error**
            if status_name is not None:
                status_name = status_name.lower()  # Ensure it's lowercase for comparison
            else:
                status_name = "no status"

            appointment_data = {
                "id": appointment.appointment_id,
                "date": formatted_date,
                "time": formatted_time,
                "name": appointment.user.name,
                "phone": appointment.user.phone,
                "services": service_details,
                "amount": total_amount,
                "status": status_name,
                "status_id": status_id,
                "modify_status": status_name,
                "location": city,
                "stylist": stylist_name,
                "stylist_id": stylist_id,
                "payment_status": payment_status,
                "provider_id": appointment.provider.provider_id if appointment.provider else None,
                "provider_name": provider_name
            }

            # **Only add cancellation_message when status_id == 4**
            if status_id == 4:
                message_obj = Message.objects.filter(message_id=appointment.message).first()
                appointment_data["cancellation_message"] = message_obj.text if message_obj else "No message"

            data.append(appointment_data)

        return paginator.get_paginated_response(data)




# All Sales and Transactions List
class AllSalesTransactionAPIView(APIView, CustomPagination):
    def get(self, request):
        provider_id = request.query_params.get('provider_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        pay_id = request.query_params.get('pay_id')
        provider_name = request.query_params.get('provider_name')
        mobile_number = request.query_params.get('mobile_number')

        query = """
        SELECT 
            pt.id,  
            pt.provider_id,  -- Include provider_id
            pt.date,
            pt.amount,
            pt.type,
            pt.payment_type,
            pt.transaction_id,
            pt.order_id,
            pt.total_amount,
            pt.status,
            pt.pay_id,
            pt.cgst,
            pt.sgst,
            sp.name AS provider_name,
            sp.owner_name,
            sp.phone AS provider_phone,
            pt.payment_type AS payment_mode,
            st.type_name AS service_type
        FROM provider_transactions pt
        INNER JOIN serviceproviders sp ON pt.provider_id = sp.provider_id
        INNER JOIN beautyapp_servicetypes st ON sp.service_type_id = st.service_type_id
        WHERE pt.status = 'Success'
        """

        params = []

        if provider_id:
            query += " AND pt.provider_id = %s"
            params.append(provider_id)

        if start_date:
            query += " AND pt.date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND pt.date <= %s"
            params.append(end_date)

        if pay_id:
            query += " AND pt.pay_id LIKE %s"
            params.append(f"%{pay_id}%")

        if provider_name:
            query += " AND sp.name LIKE %s"
            params.append(f"%{provider_name}%")

        if mobile_number:
            query += " AND (sp.phone LIKE %s OR sp.phone LIKE %s)"
            params.append(f"{mobile_number}%")
            params.append(f"%{mobile_number}")

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "provider_id": row[1],  # Include provider_id in response
                "date": row[2],
                "amount": float(row[3]),
                "credits": float(row[3]),  
                "type": row[4],
                "payment_type": row[5],
                "transaction_id": row[6],
                "order_id": row[7],
                "total_amount": float(row[8]),
                "status": row[9],
                "pay_id": row[10],
                "cgst": float(row[11]),
                "sgst": float(row[12]),
                "provider_name": row[13],
                "owner_name": row[14],
                "provider_phone": row[15],
                "payment_mode": row[16],
                "service_type": row[17]
            })

        paginated_data = self.paginate_queryset(data, request, view=self)
        return self.get_paginated_response(paginated_data)


#Get Coupon List
class CouponListAPIView(generics.ListAPIView):
    queryset = Coupon.objects.filter(is_deleted=False).order_by('-id')  # Exclude deleted coupons
    serializer_class = CouponSerializer
    pagination_class = CustomPagination  # Enable pagination

    def get(self, request, *args, **kwargs):
        coupons = self.get_queryset()

        # Optional filters for status or month
        status_filter = request.query_params.get('status')
        month_filter = request.query_params.get('month')

        if status_filter:
            coupons = coupons.filter(status=status_filter)

        if month_filter:
            try:
                month_number = datetime.strptime(month_filter, "%B").month
                coupons = coupons.filter(valid_from__month=month_number)
            except ValueError:
                return Response(
                    {"status": "failure", "message": "Invalid month format. Use full month name."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Apply pagination
        page = self.paginate_queryset(coupons)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "status": "success",
                "message": "Coupons fetched successfully",
                "data": serializer.data
            })

        serializer = self.get_serializer(coupons, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)


#Expired Coupon List
class ExpiredCouponListAPIView(generics.ListAPIView):
    serializer_class = CouponSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        """Fetch only expired and non-deleted coupons."""
        today = datetime.today().date()
        return Coupon.objects.filter(valid_until__lt=today, is_deleted=False)

    def get(self, request, *args, **kwargs):
        """Return expired coupons with pagination."""
        expired_coupons = self.get_queryset()

        # Apply pagination
        page = self.paginate_queryset(expired_coupons)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "status": "success",
                "message": "Expired coupons fetched successfully",
                "data": serializer.data
            })

        serializer = self.get_serializer(expired_coupons, many=True)
        return Response({
            "status": "success",
            "message": "Expired coupons fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

#Coupon Add
class CouponCreateAPIView(generics.CreateAPIView):
    serializer_class = CouponsSerializer

    def create(self, request, *args, **kwargs):
        """Handles coupon creation"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Coupon created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "error",
            "message": "Failed to create coupon",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

#Coupon Edit    
class CouponUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CouponsSerializer
    queryset = Coupon.objects.filter(is_deleted=False)  # Exclude deleted coupons

    def update(self, request, *args, **kwargs):
        """Handles updating a coupon by ID from query parameters"""
        coupon_id = request.query_params.get('id')  # Get ID from query params
        if not coupon_id:
            return Response({"status": "error", "message": "Coupon ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        coupon = get_object_or_404(Coupon, id=coupon_id, is_deleted=False)  # Fetch only non-deleted coupon
        serializer = self.get_serializer(coupon, data=request.data, partial=True)  # Allow partial updates

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "message": "Coupon updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"status": "error", "message": "Failed to update coupon", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


#Coupon Delete   
class CouponDeleteAPIView(generics.DestroyAPIView):
    """Soft delete a coupon by marking is_deleted=True"""
    
    def delete(self, request, *args, **kwargs):
        coupon_id = request.query_params.get('id')  # Get coupon ID from query params
        
        if not coupon_id:
            return Response({"status": "error", "message": "Coupon ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        coupon = get_object_or_404(Coupon, id=coupon_id)

        # Perform soft delete
        coupon.is_deleted = True
        coupon.save()

        return Response({"status": "success", "message": "Coupon deleted successfully"}, status=status.HTTP_200_OK)

#Delete Service Provider
class DeleteServiceProvider(APIView):
    def delete(self, request):
        provider_id = request.query_params.get('provider_id')

        if not provider_id:
            return Response({
                "status": "failure",
                "message": "Provider ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            provider = ServiceProvider.objects.get(provider_id=provider_id, is_deleted=False)

            # Soft delete (mark as deleted)
            provider.is_deleted = True
            provider.save()

            return Response({
                "status": "success",
                "message": "Service provider deleted successfully."
            }, status=status.HTTP_200_OK)

        except ServiceProvider.DoesNotExist:
            return Response({
                "status": "failure",
                "message": "Service provider not found."
            }, status=status.HTTP_404_NOT_FOUND)

