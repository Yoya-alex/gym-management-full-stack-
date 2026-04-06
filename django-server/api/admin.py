from django.contrib import admin
from .models import User, Member, Trainer, SportType, Schedule, Payment, Notification, Product

admin.site.register(User)
admin.site.register(Member)
admin.site.register(Trainer)
admin.site.register(SportType)
admin.site.register(Schedule)
admin.site.register(Payment)
admin.site.register(Notification)
admin.site.register(Product)
