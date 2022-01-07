from django.urls import path
from . import views

urlpatterns = [

    path('history/<str:puserid>', views.history),
    path('callback', views.callback),
]

# path('callback', views.callback),