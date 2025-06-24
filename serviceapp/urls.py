from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginViewSet,RegisterServiceProvider, ProviderBankInfo,ProviderTaxInfo,ProviderGeneralInfo,RoleViewSet,StaffManagementAPIView,StaffDetailAPIView,BranchesByProviderAPIView,BranchListCreateView,BranchDetailView, BranchListView,ReviewViewSet,ServicesViewSet, AddServicesAPIView,ActiveServicesView,ProviderServicesView,EditServiceAPIView,DeleteServiceAPIView,PermissionsAPIView,RoleProviderPermissionsAPIView, AppointmentListView, StatusViewSet,CategoryViewSet,SubcategoryViewSet,ServicesByCategorySubcategoryView,UpdateActiveServicesView,BeauticianViewSet,AssignStylistView,SalesTransactionAPIView,get_invoice_view,generate_invoice_pdf,CopyBranchServicesAPIView,ModifyAppointmentStatus,ProviderTransactionListView,ReviewApprovalAPIView,AddWalletTransactionView,CreditsView,PackageDetailsView,AddPackageServiceView,EditPackageServiceView, DeletePackageServiceView,ActivePackagesByProviderView,ServiceProviderListView,ProviderDetailsView, UpdateActivePackagesView,SuperAdminLoginViewSet,UpdateServiceProviderStatus,UpdateProviderDetails,StylistListView,toggle_service_status,update_service_status,UpdatePaymentStatus,CancelAppointmentView,ProviderBranchesCityView,CreateOrderView,VerifyPaymentView,CreateWalletTransactionView,EditAppointmentView,CancelPaymentView,SuperAdminBookingListAPIView,category_list,add_category,edit_category,delete_category,get_subcategories,add_subcategory,edit_subcategory,delete_subcategory,get_services,add_service,edit_service,delete_service,ReviewListView, AllAppointmentsListView,AllSalesTransactionAPIView,CouponListAPIView,ExpiredCouponListAPIView,CouponCreateAPIView,CouponUpdateAPIView,CouponDeleteAPIView,DeleteServiceProvider,generate_sales_transaction_pdf,DownloadSalesTransactionCSVAPIView,DownloadAllSalesTransactionCSVAPIView, ProviderWalletManagementView,AddProviderCreditsView,CouponStatsAPIView,WalletManagementView,ProviderTransactionDetailAPIView, CancelAppointmentByProviderAPIView,UploadProviderFiles,ProviderCategoryView
from .views import DashboardActiveStatusAPIView,UserListView
from .views import CallbackRequestListView

router = DefaultRouter()
router.register(r'login', LoginViewSet, basename='login')
router.register(r'provider_roles', RoleViewSet, basename='role')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'services',ServicesViewSet)
router.register(r'status', StatusViewSet, basename='status')
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubcategoryViewSet)
router.register(r'beauticians', BeauticianViewSet, basename='beauticians')
router.register(r'superadmin', SuperAdminLoginViewSet, basename='superadmin-login')



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
    path('provider_services/', ServicesByCategorySubcategoryView.as_view(), name='services-by-category-subcategory'),
    path('update-active-services/', UpdateActiveServicesView.as_view(), name='update-active-services'),
    path('assign-stylist/', AssignStylistView.as_view(), name='assign-stylist'),
    path('sales-transactions/', SalesTransactionAPIView.as_view(), name='sales-transactions'),
    path('invoice/', get_invoice_view, name='get_invoice'),
    path('generate-invoice-pdf/', generate_invoice_pdf, name='generate_invoice_pdf'),
    path("copy-services/", CopyBranchServicesAPIView.as_view(), name="copy-services"),
    path('modify-status/', ModifyAppointmentStatus.as_view(), name='modify_appointment_status'),
    path('provider-transactions/', ProviderTransactionListView.as_view(), name='transaction-list'),
    path('approve-review/', ReviewApprovalAPIView.as_view(), name='approve-review'),
    path('add-wallet-transaction/', AddWalletTransactionView.as_view(), name='add-wallet-transaction'),
    path('wallet-credits/', CreditsView.as_view(), name='provider-credits'),
    path('packages-list/', PackageDetailsView.as_view(), name='package_details'),
    path('add-package-service/', AddPackageServiceView.as_view(), name='add_package_service'),
    path('edit-package/', EditPackageServiceView.as_view(), name='edit-package-service'),
    path('delete-package/', DeletePackageServiceView.as_view(), name='soft-delete-package'),
    path('active-packages/', ActivePackagesByProviderView.as_view(), name='active-packages-by-provider'),
    path('update-packages/', UpdateActivePackagesView.as_view(), name='update-service'),
    path('providers_list/', ServiceProviderListView.as_view(), name='service_provider_list'),
    path('general_info/', ProviderDetailsView.as_view(), name='provider-details'),
    path('accept-provider-status/', UpdateServiceProviderStatus.as_view(), name='update-provider-status'),
    path('update-provider-details/', UpdateProviderDetails.as_view(), name='update-provider-details'),
    path('stylists/', StylistListView.as_view(), name='stylist-list'),
    path('toggle-service-status/', toggle_service_status, name="toggle_service_status"),
    path('update-service-status/', update_service_status, name='update-service-status'),
    path("update-payment-status/", UpdatePaymentStatus.as_view(), name="update-payment-status"),
    path('cancel-appointment/', CancelAppointmentView.as_view(), name='cancel-appointment'),
    path('provider_cities/', ProviderBranchesCityView.as_view(), name='provider-branches-city'),
    path("create-order/", CreateOrderView.as_view(), name="create-order"),
    path("verify-payment/", VerifyPaymentView.as_view(), name="verify-payment"),
    path('cancel-payment/', CancelPaymentView.as_view(), name='cancel_payment'),
    path('wallet/add-transaction/', CreateWalletTransactionView.as_view(), name='add-wallet-transaction'),
    path('edit-appointment/', EditAppointmentView.as_view(), name='edit-appointment'),
    path('getbookings/', SuperAdminBookingListAPIView.as_view(), name='superadmin-booking-list'),
    path('category/', category_list, name='category-list'),  
    path('category/add/', add_category, name='add-category'),
    path('category/edit/', edit_category, name='edit-category'),
    path('category/delete/', delete_category, name='delete-category'),
    path('subcategory/', get_subcategories, name='subcategory-list'),
    path('subcategory/add/', add_subcategory, name='subcategory-add'),
    path('subcategory/edit/', edit_subcategory, name='subcategory-edit'),
    path('subcategory/delete/', delete_subcategory, name='subcategory-delete'),
    path('get_services/', get_services, name='get_services'),
    path('add_service/', add_service, name='add_service'),
    path('edit_service/', edit_service, name='edit_service'),
    path('delete_service/', delete_service, name='delete_service'),
    path('review-list/', ReviewListView.as_view(), name='review-list'),
    path('getappointments/', AllAppointmentsListView.as_view(), name='superadmin-booking-list'),
    path('get-sales-transactions/', AllSalesTransactionAPIView.as_view(), name='sales-transactions'),
    path('get-coupons/', CouponListAPIView.as_view(), name='get-coupons'),
    path('coupons/expired/', ExpiredCouponListAPIView.as_view(), name='expired-coupons'),
    path('coupons/add/', CouponCreateAPIView.as_view(), name='add-coupon'),
    path('coupons/edit/', CouponUpdateAPIView.as_view(), name='edit_coupon'),
    path('coupons/delete/', CouponDeleteAPIView.as_view(), name='edit_coupon'),
    path('delete-service-provider/', DeleteServiceProvider.as_view(), name='delete_service_provider'),
    path('provider-invoice/', generate_sales_transaction_pdf, name='generate_sales_transaction_pdf'),
    path('download-user-transactions/', DownloadSalesTransactionCSVAPIView.as_view(), name='download_sales_transactions'),
    path('download-provider-transactions/', DownloadAllSalesTransactionCSVAPIView.as_view(), name='download_all_sales_transactions'),
    path('provider-wallet/', ProviderWalletManagementView.as_view(), name='wallet-management'),
    path('add-credits/', AddProviderCreditsView.as_view(), name='add-credits'),
    path('coupon_counts/', CouponStatsAPIView.as_view(), name='get_coupon_stats'),
    path('wallet-counts/', WalletManagementView.as_view(), name='wallet_management'),
    path('get-provider-transaction/', ProviderTransactionDetailAPIView.as_view(), name='provider-transaction'),
    path('cancel-appointment-by-provider/', CancelAppointmentByProviderAPIView.as_view(), name='cancel-appointment-by-provider'),
    path('upload-tax-files/', UploadProviderFiles.as_view(), name='upload-tax-files'),
    path('provider_category/', ProviderCategoryView.as_view(), name='provider-categories'),
    path('dashboard/active-status/', DashboardActiveStatusAPIView.as_view(), name='dashboard_active_status'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('callback-requests-list/', CallbackRequestListView.as_view(), name='callback-list'),



]
