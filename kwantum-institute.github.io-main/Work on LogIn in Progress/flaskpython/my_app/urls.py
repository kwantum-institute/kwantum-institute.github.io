from django.urls import path
from .views import DataAPIView

urlpatterns = [
    path('api/data/', DataAPIView.as_view(), name='data-api'),
]
