from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from django.utils import timezone
from rest_framework.decorators import action
import random
import string
from .models import ServiceProvider,ProviderBankDetails,ProviderTaxRegistration,Role,Staff,Branches,Locations,Review,Category,Subcategory,Services,Serviceprovidertype,Permissions,Appointment,Status
from .serializers import LoginSerializer,ServiceProviderSerializer,ProviderBankDetailsSerializer,ProviderTaxRegistrationSerializer,SalonDetailsSerializer,FreelancerDetailsSerializer,RoleSerializer,StaffSerializer,StaffCreateSerializer,BranchSerializer,BranchesSerializer,BranchListSerializer,ReviewSerializer,ServicesSerializer,ServiceSerializer,PermissionsSerializer,CreatePermissionsSerializer,StatusSerializer,ProviderSerializer,ServiceprovidertypeSerializer,ServiceProvidersSerializer
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


class LoginViewSet(viewsets.ModelViewSet):
    # queryset = ServiceProvider.objects.all()
    # serializer_class = LoginSerializer

    # Override the create method for initiating login (generating OTP)
    def create(self, request, *args, **kwargs):
        phone = request.data.get('phone')  # Get phone number from request
        
        if not phone:
            return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create the Login entry for the phone number
        #login_entry = ServiceProvider.objects.get(phone=phone)
        try:
            # Fetch the ServiceProvider entry with the given phone number
            login_entry = ServiceProvider.objects.get(phone=phone)
        except ServiceProvider.DoesNotExist:
            # Handle case where the phone number does not exist
            return Response({'status': 'failure', 'message': 'Provided mobile number does not exist'}, status=status.HTTP_404_NOT_FOUND)

        login_entry.otp = '1234'  # Default OTP value
        login_entry.otp_created_at = timezone.now()  # This will correctly use the current date-time in UTC
        login_entry.save()

        message = 'OTP updated successfully'

        # Return the OTP (In a real app, you'd send it via SMS)
        return Response({'status': 'success','otp': login_entry.otp, 'message': message}, status=status.HTTP_200_OK)

    # Define a custom action for verifying OTP
    
    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request, *args, **kwargs):
        phone = request.data.get('phone')  # Get phone number from request
        otp = request.data.get('otp')  # Get OTP from request
        
        if not phone or not otp:
            return Response({'status': 'failure', 'message': 'Phone and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            login_entry = ServiceProvider.objects.get(phone=phone)
        except ServiceProvider.DoesNotExist:
            return Response({'status': 'failure', 'message': 'Invalid phone number'}, status=status.HTTP_404_NOT_FOUND)
    
        # Check if the OTP matches
        if login_entry.otp == int(otp):
            # Generate a random token manually
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
    
            # Optionally, save the token to the login entry (if you choose to store it)
            # login_entry.token = token
            # login_entry.save()
    
            # Return the provider_id along with success message and token
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'token': token,
                'provider_id': login_entry.provider_id  # Add provider_id to the response
            }, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'failure', 'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

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
                {"message": "Service Provider registered successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_200_OK)
    
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
            serializer.save()
            return Response({"message": "Tax registration details saved successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_200_OK)



class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows roles to be viewed or edited.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_queryset(self):
        """
        Optionally filter roles based on active status.
        """
        status = self.request.query_params.get('status', None)
        if status is not None:
            return self.queryset.filter(status=status.lower() in ['true', '1'])
        return self.queryset

#Staff Management
class StaffManagementAPIView(APIView):
    def get(self, request, provider_id=None):
        # Retrieve staff members filtered by provider_id if provided, and not marked as deleted
        if provider_id:
            staff_queryset = Staff.objects.filter(provider__provider_id=provider_id, is_deleted=False)
        else:
            staff_queryset = Staff.objects.filter(is_deleted=False)

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
            return Response({"detail": "Staff ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the staff record
            staff = Staff.objects.get(staff=staff_id)
        except Staff.DoesNotExist:
            return Response({"detail": "Staff not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the role field
        role_id = request.data.get("role")
        if role_id:
            try:
                role = Role.objects.get(role_id=role_id)
                staff.role = role
            except Role.DoesNotExist:
                return Response({"detail": "Role not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the provider field
        provider_id = request.data.get("provider")
        if provider_id:
            try:
                provider = ServiceProvider.objects.get(provider_id=provider_id)
                staff.provider = provider
            except ServiceProvider.DoesNotExist:
                return Response({"detail": "Provider not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the photo field
        photo = request.FILES.get("photo")
        if photo:
            staff.photo = photo

        # Update the name field
        staff.name = request.data.get("name", staff.name)

        # Save the updated staff record
        staff.save()

        return Response({"detail": "Staff updated successfully."}, status=status.HTTP_200_OK)

    def delete(self, request):
        # Retrieve the staff_id from the request body
        staff_id = request.data.get("staff_id")
        if not staff_id:
            return Response({"detail": "Staff ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the staff record
            staff = Staff.objects.get(staff=staff_id)
        except Staff.DoesNotExist:
            return Response({"detail": "Staff not found."}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete: mark as deleted
        staff.is_deleted = True
        staff.save()

        return Response({"detail": "Staff marked as deleted."}, status=status.HTTP_204_NO_CONTENT)
    
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
        # Filter branches by provider_id
        branches = Branches.objects.filter(provider_id=provider_id)

        if not branches.exists():
            return Response(
                {"status": "error", "message": "No branches found for this provider."},
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
            branch_queryset = Branches.objects.filter(provider__provider_id=provider_id, is_deleted=False)
        else:
            branch_queryset = Branches.objects.filter(is_deleted=False)

        # Apply search if a search query is provided
        if search_query:
            branch_queryset = branch_queryset.filter(
                Q(branch_name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(location__city__icontains=search_query)
            )

        # Paginate the queryset
        paginator = CustomPagination()
        paginated_branches = paginator.paginate_queryset(branch_queryset, request)

        # Serialize the paginated data
        serializer = BranchListSerializer(paginated_branches, many=True)

        return paginator.get_paginated_response({
            "status": "success",
            "data": serializer.data
        })

class BranchListCreateView(APIView):

    def post(self, request):
        # Extract data from the request body
        branch_name = request.data.get('branch_name')
        phone = request.data.get('branch_phone_number')  # Get phone number from request
        branch_address = request.data.get('branch_address')  # This will contain address_line1
        branch_location = request.data.get('branch_location')  # This will contain city
        logo = request.data.get('logo')

        # Check if both branch_address and branch_location are provided
        if not branch_address or not branch_location:
            return Response({"error": "Both branch_address and branch_location are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Use get_or_create to ensure location exists and retrieve its ID
        location, created = Locations.objects.get_or_create(
            city=branch_location,
            address_line1=branch_address,
            defaults={
                "address_line2": "",
                "state": None,
                "postal_code": None,
                "country": None,
                "latitude": None,
                "longitude": None,
            }
        )

        # Log whether a new location was created or an existing one was found
        if created:
            print(f"New location created with ID: {location.location_id}")
        else:
            print(f"Existing location found with ID: {location.location_id}")

        # Prepare branch data with location_id
        branch_data = {
            'branch_name': branch_name,
            'phone': phone,  # Ensure phone is passed correctly
            'logo': logo,
            'location': location.location_id  # Pass the location_id here
        }
        print("Prepared Branch Data:", branch_data)
 

        # Use the serializer to save the branch data
        serializer = BranchesSerializer(data=branch_data)
        if serializer.is_valid():
            # Save the branch object
            serializer.save()
            return Response({"message": "Branch created successfully!"}, status=status.HTTP_201_CREATED)

        # If validation fails, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




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
            return Response({"error": "Branch ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        branch = self.get_object(branch_id)
        if not branch:
            return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BranchListSerializer(branch)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        # Retrieve `branch_id` from the request body
        branch_id = request.data.get("branch_id")
        if not branch_id:
            return Response({"error": "Branch ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        branch = self.get_object(branch_id)
        if not branch:
            return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)

        # Combine request data with any uploaded files
        data = request.data.copy()  # Use `copy()` for mutable data
        if request.FILES:
            data.update(request.FILES)

        # If 'location' field is provided as city name, find the corresponding location_id
        if 'location' in data:
            city_name = data.get('location')
            try:
                location = Locations.objects.get(city=city_name)  # Retrieve location by city name
                data['location'] = location.location_id  # Set the location_id (primary key)
            except Locations.DoesNotExist:
                return Response({"error": "Location with city name '{}' not found.".format(city_name)}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BranchesSerializer(branch, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Branch updated successfully!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Retrieve `branch_id` from the request body
        branch_id = request.data.get("branch_id")
        if not branch_id:
            return Response({"error": "Branch ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        branch = self.get_object(branch_id)
        if not branch:
            return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Perform soft delete
        branch.is_deleted = True
        branch.save()
        
        return Response({"message": "Branch deleted successfully!"}, status=status.HTTP_200_OK)




#Report & Rating
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination  # Use custom pagination

    def get_queryset(self):
        # Filter reviews based on provider_id
        provider_id = self.request.query_params.get('provider_id')
        if provider_id:
            return Review.objects.filter(provider_id=provider_id)
        return Review.objects.all()

class ServicesViewSet(viewsets.ModelViewSet):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer

class AddServicesAPIView(APIView):
    def post(self, request):
        try:
            with transaction.atomic():
                # Extract data from the request
                provider_id = request.data.get('provider_id')
                branch_id = request.data.get('branch_id')
                category_id = request.data.get('category_id')
                subcategory_id = request.data.get('subcategory_id')
                service_ids = request.data.get('service_ids')  # List of selected services
                price = request.data.get('price')
                duration = request.data.get('duration')

                if not all([provider_id, branch_id, category_id, subcategory_id, service_ids]):
                    return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

                # Loop through selected services and add them to Serviceprovidertype
                for service_id in service_ids:
                    Serviceprovidertype.objects.create(
                        provider_id_id=provider_id,
                        branch_id=branch_id,
                        service_id_id=service_id,
                        price=price,
                        duration=duration,
                        status='Active'
                    )

                return Response({'message': 'Services added successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ActiveServicesView(APIView):
    def get(self, request, *args, **kwargs):
        provider_id = request.query_params.get("provider_id")
        if not provider_id:
            return Response({"error": "provider_id is required"}, status=400)

        response_data = {}
        categories = Category.objects.filter(status="Active")

        for category in categories:
            subcategories = Subcategory.objects.filter(category=category, status="Active")
            response_data[category.category_name] = {}

            for subcategory in subcategories:
                recent_service_providers = (
                    Serviceprovidertype.objects.filter(
                        service_id__category=category,
                        service_id__subcategory=subcategory,
                        provider_id=provider_id,
                        status="Active",
                        is_deleted=False  # Exclude deleted services
                    )
                    .order_by("-provider_service_id")[:2]
                )

                response_data[category.category_name][subcategory.subcategory_name] = [
                    {
                        "service_name": service.service_id.service_name,
                        "sku_value": service.service_id.sku_value,
                        "price": service.price,
                        "service_time": service.service_id.service_time,
                    }
                    for service in recent_service_providers
                ]

        return Response(response_data)


class ProviderServicesView(APIView):
    # Set the pagination class
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['service_name']  # Fields to search by, e.g., searching by service name

    def get(self, request):
        provider_id = request.query_params.get('provider_id', None)

        if not provider_id:
            return Response({"error": "provider_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Filter services based on provider_id
            services = Serviceprovidertype.objects.filter(provider_id=provider_id,is_deleted=False)

            # If no services are found, return a message
            if not services.exists():
                return Response({"message": "No services found for this provider."}, status=status.HTTP_404_NOT_FOUND)

            # Apply pagination
            paginator = CustomPagination()
            result_page = paginator.paginate_queryset(services, request)
            if result_page is not None:
                return paginator.get_paginated_response(self.serialize_services(result_page))

            # In case pagination is not applied
            return Response(self.serialize_services(services), status=status.HTTP_200_OK)

        except Serviceprovidertype.DoesNotExist:
            return Response({"error": "Provider not found"}, status=status.HTTP_404_NOT_FOUND)

    def serialize_services(self, services):
        """
        Serializes the list of services.
        """
        service_data = []
        for service_provider in services:
            service = service_provider.service_id  # Get the service linked to this provider
            service_data.append({
                'service_id': service.service_id,
                'service_name': service.service_name,
                'category': service.category.category_name if service.category else None,  # Access related category
                'subcategory': service.subcategory.subcategory_name if service.subcategory else None,  # Access related subcategory
                'price': service.price,
                'service_time': service.service_time,
                'status': service.status,
                'sku_value': service.sku_value
            })
        return service_data
    
class EditServiceAPIView(APIView):
    def put(self, request):
        try:
            with transaction.atomic():
                # Extract provider_service_id from the request body
                provider_service_id = request.data.get("provider_service_id")
                if not provider_service_id:
                    return Response({"error": "Provider service ID is required."}, status=status.HTTP_400_BAD_REQUEST)

                # Extract data from the request
                price = request.data.get("price")
                duration = request.data.get("duration")
                status_value = request.data.get("status")  # Avoid conflict with `status` module

                # Validate the input data
                if price is None and duration is None and status_value is None:
                    return Response({"error": "No fields to update."}, status=status.HTTP_400_BAD_REQUEST)

                # Fetch the Serviceprovidertype object
                service = Serviceprovidertype.objects.filter(
                    provider_service_id=provider_service_id, is_deleted=False
                ).first()

                if not service:
                    return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

                # Update the service fields if provided
                if price is not None:
                    service.price = price
                if duration is not None:
                    service.duration = duration
                if status_value is not None:
                    service.status = status_value

                # Save the updated service
                service.save()

                return Response({"message": "Service updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteServiceAPIView(APIView):
    def delete(self, request):
        try:
            # Extract provider_service_id from the request body
            provider_service_id = request.data.get("provider_service_id")
            if not provider_service_id:
                return Response({"error": "Provider service ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the Serviceprovidertype object
            service = Serviceprovidertype.objects.filter(provider_service_id=provider_service_id).first()

            if not service:
                return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

            # Mark as deleted and update status
            service.is_deleted = True
            service.status = "Inactive"
            service.save()

            return Response({"message": "Service marked as deleted successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
#Role management
class PermissionsAPIView(APIView):
      def post(self, request):
        # Get provider_id, role_id and other data from the request
        provider_id = request.data.get('provider')
        role_id = request.data.get('role')

        # Check if a permission for the given provider_id and role_id exists
        permission = Permissions.objects.filter(provider_id=provider_id).first()

        if permission:
            # If permission exists, update it with the new data
            serializer = PermissionsSerializer(permission, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Permissions updated successfully!'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = CreatePermissionsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Permissions added successfully!'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoleProviderPermissionsAPIView(APIView):
    def get(self, request, provider_id):
        # Retrieve all permissions related to the provider
        permissions = Permissions.objects.filter(provider_id=provider_id)

        if permissions.exists():
            # Serialize and return the data if found
            serializer = PermissionsSerializer(permissions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'No permissions found for this provider.'}, status=status.HTTP_404_NOT_FOUND)


class AppointmentListView(APIView):
    """
    API to list appointments for a given provider_id and optional status
    """

    def get(self, request, *args, **kwargs):
        provider_id = request.GET.get('provider_id')
        status_filter = request.GET.get('status')  # Get optional status filter

        if not provider_id:
            return JsonResponse(
                {"status": "error", "message": "provider_id is required"},
                status=400
            )

        # If a status filter is provided, filter by both provider_id and status_id
        if status_filter:
            appointments = Appointment.objects.filter(provider_id=provider_id, status__status_id=status_filter)
        else:
            appointments = Appointment.objects.filter(provider_id=provider_id)

        # Paginate the results
        paginator = CustomPagination()
        paginated_appointments = paginator.paginate_queryset(appointments, request)

        # Serialize data into JSON-friendly format
        data = []
        for appointment in paginated_appointments:
            # Extract service IDs from `service_id_new` field
            service_ids = appointment.service_id_new.split(",") if appointment.service_id_new else []
            
            # Fetch the services from the database
            services = Services.objects.filter(service_id__in=service_ids)
            
            # Serialize service details into an array of arrays
            service_details = [
                {"name": service.service_name, "price": float(service.price) if service.price else 0}
                for service in services
            ]
            
            # Calculate the total amount
            total_amount = sum(float(service["price"]) for service in service_details)

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
                location = getattr(appointment.branch, 'location', None)  # Safely get the location
                if location:
                    city = location.city

            # Append serialized data
            data.append({
                "id": appointment.appointment_id,
                "date": formatted_date,  
                "time": formatted_time,  
                "name": appointment.user.name,
                "phone": appointment.user.phone,
                "services": service_details,  # Array of service details
                "amount": total_amount,  
                "status": appointment.status.status_name,  # Get status name from Status model
                "modify_status": appointment.status.status_name,
                "location": city,  
            })

        # Return paginated response
        return paginator.get_paginated_response(data)
    
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
    
class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ProviderSerializer

    def get_queryset(self):
        category_id = self.request.query_params.get('category_id', None)

        if category_id:
            # Ensure correct field names and relationships are used
            return ServiceProvider.objects.filter(
                provider_id__in=Serviceprovidertype.objects.filter(
                    service_id__in=Services.objects.filter(category_id=category_id)
                ).values_list('provider_id', flat=True)
            )

        # Return all service providers if no category_id is provided
        return super().get_queryset()
    

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
     category_id = request.query_params.get('category_id')
     address = request.query_params.get('address') or "Trivandrum"  
     radius = request.query_params.get('radius') or 20 
     service_type_id = request.query_params.get('service_type_id')
     open_now = request.query_params.get('open_now')  # 0 is closed, 1 is open
 
     # Check only for category_id as a required field
     if not category_id:
         return Response(
             {
                 "status": "failure",
                 "message": "Missing required query parameter: category_id",
                 "data": []
             },
             status=status.HTTP_400_BAD_REQUEST
         )
 
     try:
         # Handle optional address and radius parameters
         if address and radius:
             # Get latitude and longitude from the provided address (assuming you have a method for this)
             lat, lng = self.get_lat_lng(address)
         else:
             # Default latitude and longitude, or skip filtering by location if no address/radius is provided
             lat, lng = None, None
 
         # Use the model class to call the method
         results = Serviceprovidertype().get_provider_services_with_cursor(
             category_id, lat, lng, radius, service_type_id
         )
 
         if results:
             return Response(
                 {
                     "status": "success",
                     "message": "Filtered service providers retrieved successfully",
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
                 "message": "Failed to retrieve service providers",
                 "error": str(e),
                 "data": []
             },
             status=status.HTTP_404_NOT_FOUND
         )
 