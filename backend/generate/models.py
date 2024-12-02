from django.db import models

# Create your models here.

class Picture(models.Model):
    uploaded_picture = models.ImageField(upload_to='picture/uploaded/')
    enhanced_picture = models.ImageField(upload_to='picture/enhanced/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
