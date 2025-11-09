from django.urls import path
from .views import RecariaDashboardView

app_name = 'recaria'

urlpatterns = [
    path('dashboard/', RecariaDashboardView.as_view(), name='dashboard'),
]
