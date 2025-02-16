
from django.urls import path,include
from .views import ServiceProviderSearchAPIView,FilterAPIView
from rest_framework.routers import DefaultRouter
from .views import ServiceProviderViewSet
from .views import ServiceTypesViewSet
from .views import BeauticianViewSet
from .views import PhotoViewSet
from .views import FAQViewSet
from .views import UserViewSet
from .views import StaffViewSet
from .views import ServiceprovidertypeViewSet
from .views import ServicesViewSet
from .views import StaffReviewViewSet
from .views import AppointmentViewSet
from .views import PaymentViewSet
from .views import CustomerFeedbackViewSet
from .views import CategoryViewSet
from .views import SubcategoryViewSet
from .views import BookServiceViewSet
from .views import LoginViewSet
from .views import AvailableSlotsViewSet
from .views import ReviewViewSet
from .views import CouponAPIView, VerifyCouponAPIView
from .views import ServiceFAQViewSet
from .views import AddToCartAPIView,AddPaymentAPIView,OTPVerificationAPIView,BookingListAPIView,ProviderActionAPIView,AppointmentStatusAPIView

router = DefaultRouter()
router.register(r'service-providers', ServiceProviderViewSet, basename='serviceprovider')
router.register(r'service-types', ServiceTypesViewSet)
router.register(r'stylists', BeauticianViewSet)
router.register(r'photos', PhotoViewSet)
router.register(r'faqs', FAQViewSet)
router.register(r'user',UserViewSet )
router.register(r'staff', StaffViewSet)
router.register(r'serviceprovidertypes', ServiceprovidertypeViewSet)
router.register(r'services',ServicesViewSet)
router.register(r'staffreviews', StaffReviewViewSet, basename='staffreview')
router.register(r'appointments', AppointmentViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'customer-feedback', CustomerFeedbackViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubcategoryViewSet)
router.register(r'bookservice', BookServiceViewSet,basename='bookservice')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'available-slots', AvailableSlotsViewSet, basename='available-slots')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'servicefaq', ServiceFAQViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search/', ServiceProviderSearchAPIView.as_view(), name='service-provider-search'),
    path('filter/', FilterAPIView.as_view(), name='filter'),
    path('coupon/', CouponAPIView.as_view(), name='coupon'),
    path('verify_coupon/', VerifyCouponAPIView.as_view(), name='verify_coupon'),
    path('book_now/', AddToCartAPIView.as_view(), name='store_user_cart'),
    path('bookings/', BookingListAPIView.as_view(), name='booking_list'),
    path('verify_otp/', OTPVerificationAPIView.as_view(), name='verify_otp'),
    path('checkout/', AddPaymentAPIView.as_view(), name='add_payment'),
    path('provider-booking-action/', ProviderActionAPIView.as_view(), name='booking-action'),
    path('appointment/status/', AppointmentStatusAPIView.as_view(), name='appointment-status'),


]
