from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginViewSet,RegisterServiceProvider, ProviderBankInfo,ProviderTaxInfo,ProviderGeneralInfo,RoleViewSet,StaffManagementAPIView,StaffDetailAPIView,BranchesByProviderAPIView,BranchListCreateView,BranchDetailView, BranchListView,ReviewViewSet,ServicesViewSet, AddServicesAPIView,ActiveServicesView,ProviderServicesView,EditServiceAPIView,DeleteServiceAPIView,PermissionsAPIView,RoleProviderPermissionsAPIView, AppointmentListView, StatusViewSet, ServiceProviderViewSet,ServiceprovidertypeViewSet



router = DefaultRouter()
router.register(r'login', LoginViewSet, basename='login')
router.register(r'provider_roles', RoleViewSet, basename='role')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'services',ServicesViewSet)
router.register(r'status', StatusViewSet, basename='status')
router.register(r'service-providers',ServiceProviderViewSet)
router.register(r'serviceprovidertypes', ServiceprovidertypeViewSet)







urlpatterns = [
    path('', include(router.urls)),  
    path('register/', RegisterServiceProvider.as_view(), name='register-service-provider'),
    path('register_general_info/<int:provider_id>/', ProviderGeneralInfo.as_view(), name='register_general_info'),
    path('register_bank_info/', ProviderBankInfo.as_view(), name='provider_bank_info'),
    path('register_tax_info/', ProviderTaxInfo.as_view(), name='provider_tax_info'),
    path('staff-list/', StaffManagementAPIView.as_view(), name='staff_management'),
    path('staff-list/<int:provider_id>/', StaffManagementAPIView.as_view(), name='staff_by_provider'),
    path('staff/<int:staff_id>/', StaffDetailAPIView.as_view(), name='staff_detail'),
    path('staff-edit-delete/', StaffManagementAPIView.as_view(), name='staff-edit-delete'),
    path('staff-branches/<int:provider_id>/', BranchesByProviderAPIView.as_view(), name='branches-by-provider'),
    path('branches/', BranchListCreateView.as_view(), name='branch_list_create'),
    path('branch/', BranchDetailView.as_view(), name='branch_detail'),
    path('branches-list/', BranchListView.as_view(), name='branch-list'),
    path('branches-list/<int:provider_id>/', BranchListView.as_view(), name='branches-by-provider'),
    path('add-services/', AddServicesAPIView.as_view(), name='add-services'),
    path('active-services/', ActiveServicesView.as_view(), name='active_services_api'),
    path('provider-services/', ProviderServicesView.as_view(), name='provider_services'),
    path('provider-services/edit/', EditServiceAPIView.as_view(), name='edit_service'),
    path('provider-services/delete/', DeleteServiceAPIView.as_view(), name='delete_service'),
    path('permissions/', PermissionsAPIView.as_view(), name='permissions_create_or_update'),
    path('provider_permissions/<int:provider_id>/', RoleProviderPermissionsAPIView.as_view(), name='permissions_by_provider'),
    path('appointments/', AppointmentListView.as_view(), name='appointment-list'),

]
