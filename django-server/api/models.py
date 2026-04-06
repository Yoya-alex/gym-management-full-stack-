from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [('admin', 'Admin'), ('moderator', 'Moderator')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='moderator')

    class Meta:
        db_table = 'users'


class SportType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sport_pic = models.CharField(max_length=500, blank=True)
    monthly_price = models.FloatField(default=0)

    def __str__(self):
        return self.name


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
    specialization = models.CharField(max_length=200, blank=True)
    rating = models.FloatField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='member_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_pic = models.CharField(max_length=500, blank=True)
    birthday = models.DateField()
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    has_paid = models.BooleanField(default=True)
    cin = models.CharField(max_length=50, unique=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True)
    sport_type = models.ForeignKey(SportType, on_delete=models.SET_NULL, null=True, blank=True)
    membership_start = models.DateField(null=True, blank=True)
    membership_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def membership_active(self):
        if self.membership_end:
            return self.membership_end >= timezone.now().date()
        return False


class Schedule(models.Model):
    title = models.CharField(max_length=200)
    sport_type = models.ForeignKey(SportType, on_delete=models.SET_NULL, null=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True)
    start = models.CharField(max_length=50, blank=True)
    end = models.CharField(max_length=50, blank=True)
    start_time = models.CharField(max_length=20, blank=True)
    end_time = models.CharField(max_length=20, blank=True)
    days_of_week = models.JSONField(default=list, blank=True)
    capacity = models.IntegerField(default=20)
    enrolled_count = models.IntegerField(default=0)

    @property
    def is_full(self):
        return self.enrolled_count >= self.capacity


class Enrollment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='enrollments')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member', 'schedule')


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Cash'),
        ('mobile', 'Mobile'),
        ('online', 'Online'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    amount = models.FloatField(default=0)
    credit = models.FloatField(default=0)
    months = models.IntegerField(default=1)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    sport_type = models.ForeignKey(SportType, on_delete=models.SET_NULL, null=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-create notification on payment
        if self.status == 'completed':
            Notification.objects.get_or_create(
                member=self.member,
                type='payment',
                title='Payment Confirmed',
                defaults={
                    'description': f'Payment of ${self.amount} confirmed for {self.months} month(s).',
                    'is_unread': True,
                }
            )


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
