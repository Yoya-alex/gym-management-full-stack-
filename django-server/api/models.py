from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [('admin', 'Admin'), ('moderator', 'Moderator')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='moderator')

    class Meta:
        db_table = 'users'


class SportType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sport_pic = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_pic = models.CharField(max_length=500, blank=True)
    birthday = models.DateField()
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    has_paid = models.BooleanField(default=True)
    cin = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Trainer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_pic = models.CharField(max_length=500, blank=True)
    birthday = models.DateField()
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    cin = models.CharField(max_length=50, unique=True)
    sport_types = models.ManyToManyField(SportType, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Schedule(models.Model):
    title = models.CharField(max_length=200)
    sport_type = models.ForeignKey(SportType, on_delete=models.SET_NULL, null=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True)
    start = models.CharField(max_length=50, blank=True)
    end = models.CharField(max_length=50, blank=True)
    start_time = models.CharField(max_length=20, blank=True)
    end_time = models.CharField(max_length=20, blank=True)
    days_of_week = models.JSONField(default=list, blank=True)  # [0-6] for recurring


class Payment(models.Model):
    amount = models.FloatField(default=0)
    credit = models.FloatField(default=0)
    months = models.IntegerField(default=1)
    sport_type = models.ForeignKey(SportType, on_delete=models.SET_NULL, null=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True, blank=True)


class Notification(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    avatar = models.CharField(max_length=500, blank=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_unread = models.BooleanField(default=True)


class Product(models.Model):
    product_name = models.CharField(max_length=200)
    profile_pic = models.CharField(max_length=500, blank=True)
    original_price = models.FloatField(null=True, blank=True)
    colors = models.JSONField(default=list)
    our_price = models.FloatField()
    gender = models.CharField(max_length=10, blank=True)
    category = models.CharField(max_length=100, blank=True)
    qte_stock = models.IntegerField()
