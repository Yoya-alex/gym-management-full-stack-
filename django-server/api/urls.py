from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/signup', views.signup),
    path('auth/signin', views.signin),
    path('auth/changePassword', views.change_password),
    path('users', views.get_users),

    # Members
    path('members/', views.MemberListCreate.as_view()),
    path('members/<int:pk>/', views.MemberDetail.as_view()),
    path('members/card/<int:pk>/', views.member_card),

    # Trainers
    path('trainers/', views.TrainerListCreate.as_view()),
    path('trainers/<int:pk>/', views.TrainerDetail.as_view()),

    # Sport Types
    path('sportTypes/', views.SportTypeListCreate.as_view()),
    path('sportTypes/<int:pk>/', views.SportTypeDelete.as_view()),

    # Schedule
    path('schedule/', views.ScheduleListCreate.as_view()),

    # Payments
    path('payment/', views.PaymentListCreate.as_view()),

    # Notifications
    path('notifications/', views.NotificationListCreate.as_view()),

    # Products
    path('products/', views.ProductListCreate.as_view()),

    # File uploads
    path('upload/<str:model_type>/', views.upload_image),

    # Dashboard
    path('dashboard/', views.dashboard),
]
