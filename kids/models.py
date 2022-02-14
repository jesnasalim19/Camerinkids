from tabnanny import verbose
from turtle import title
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
# Notes Model
class Notes(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = "notes"
        verbose_name_plural = "notes" 

# Homework Model
class Homework(models.Model):
    user =models.ForeignKey(User,on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    description = models.TextField()
    due = models.DateTimeField()
    is_finished = models.BooleanField(default=False)
    def __str__(self):
        return self.title

# Todo Model
class Todo(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    is_finished = models.BooleanField(default=False)
    def __str__(self):
        return self.title

# Coding Section
class Coding(models.Model):
    language = models.CharField(max_length=50)
    def __str__(self):
        return self.language