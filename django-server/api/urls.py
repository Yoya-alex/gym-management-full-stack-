from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/signup', views.signup),
    path('auth/signin', views.signin),
    path('auth/changePassword', views.change_password),
    path('users', views.get_users),

    # Normal User - own profile & data
    path('me/profile', views.my_profile),
    path('me/schedule', views.my_schedule),
    path('me/payments', views.my_payments),
    path('me/notifications', views.my_notifications),
    path('me/card', views.my_card),
    path('me/enrollments', views.my_enrollments),
    path('me/enroll', views.enroll_class),
    path('me/status', views.my_membership_status),
    path('notifications/<int:pk>/read', views.mark_notification_read),

    # Members (Admin)
    path('members/', views.MemberListCreate.as_view()),
    path('members/<int:pk>/', views.MemberDetail.as_view()),
    path('members/card/<int:pk>/', views.member_card),

    # Trainers
    path('trainers/', views.TrainerListCreate.as_view()),
    path('trainers/<int:pk>/', views.TrainerDetail.as_view()),

    # Sport Types
    path('sportTypes/', views.SportTypeListCreate.as_view()),
    path('sportTypes/<int:pk>/', views.SportTypeDetail.as_view()),

    # Schedule
    path('schedule/', views.ScheduleListCreate.as_view()),
    path('schedule/<int:pk>/', views.ScheduleDetail.as_view()),

    # Payments
    path('payment/', views.PaymentListCreate.as_view()),
    path('payment/<int:pk>/invoice', views.payment_invoice),

    # Notifications
    path('notifications/', views.NotificationListCreate.as_view()),

    # Enrollments
    path('enrollments/', views.EnrollmentListCreate.as_view()),

    # Products
    path('products/', views.ProductListCreate.as_view()),

    # File uploads
    path('upload/<str:model_type>/', views.upload_image),

    # Dashboard
    path('dashboard/', views.dashboard),
]
