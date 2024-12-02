from django.urls import path
from . import views

app_name = 'generate'

urlpatterns = [
    path('upload/', views.upload_picture, name='upload'),
    path('result/<int:picture_id>/', views.result, name='result'),
]
