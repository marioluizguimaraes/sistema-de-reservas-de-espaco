from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import SalaViewSet, ReservaViewSet, RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.soap_service import soap_view 

router = DefaultRouter()
router.register(r'salas', SalaViewSet, basename='sala')
router.register(r'reservas', ReservaViewSet, basename='reserva')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('soap/', soap_view, name='soap_service'),
]