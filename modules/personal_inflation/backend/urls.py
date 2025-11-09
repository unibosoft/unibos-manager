from django.urls import path
from .views import PersonalInflationDashboardView

app_name = 'personal_inflation'

urlpatterns = [
    path('', PersonalInflationDashboardView.as_view(), name='dashboard'),
    path('dashboard/', PersonalInflationDashboardView.as_view(), name='dashboard'),
]
