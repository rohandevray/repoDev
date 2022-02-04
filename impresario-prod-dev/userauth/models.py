from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    first_name=models.CharField(max_length=200,default='')
    last_name=models.CharField(max_length=200,default='')
    gender_choice=((u'M',u'Male'),(u'F',u'Female'),(u'O',u'OTHER'))
    phone_number=models.CharField(max_length=12,default='')
    gender=models.CharField(max_length=2,choices=gender_choice,default='O')
    def __str__(self):
        return self.first_name + " "+self.last_name



class Account(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.user.username

    
