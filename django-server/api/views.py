from django.contrib.auth import authenticate
from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Member, Trainer, SportType, Schedule, Payment, Notification, Product
from .serializers import (
    UserSerializer, RegisterSerializer, MemberSerializer, TrainerSerializer,
    SportTypeSerializer, ScheduleSerializer, PaymentSerializer,
    NotificationSerializer, ProductSerializer
)
from .permissions import IsAdmin
from .utils import generate_member_card_pdf


# ── Auth ──────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    if User.objects.filter(username=request.data.get('username')).exists():
        return Response({'message': 'Username already in use!'}, status=400)
    if User.objects.filter(email=request.data.get('email')).exists():
        return Response({'message': 'Email already in use!'}, status=400)
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered successfully!'})
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def signin(request):
    user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
    if not user:
        return Response({'message': 'Invalid credentials'}, status=401)
    refresh = RefreshToken.for_user(user)
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'roles': [f'ROLE_{user.role.upper()}'],
        'accessToken': str(refresh.access_token),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = User.objects.filter(email=request.data.get('email')).first()
    if not user:
        return Response({'message': 'User not found'}, status=404)
    if not user.check_password(request.data['passwords']['curr_password']):
        return Response({'message': 'Invalid Password!'}, status=401)
    user.set_password(request.data['passwords']['password'])
    user.save()
    return Response({'message': 'Password Updated Successfully!'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = User.objects.all()
    return Response(UserSerializer(users, many=True).data)


# ── Members ───────────────────────────────────────────────────────────────────

class MemberListCreate(generics.ListCreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer


class MemberDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    http_method_names = ['get', 'patch', 'delete']


@api_view(['GET'])
def member_card(request, pk):
    member = Member.objects.filter(pk=pk).first()
    if not member:
        return Response({'error': 'Not found'}, status=404)
    pdf = generate_member_card_pdf(member)
    from django.http import HttpResponse
    return HttpResponse(pdf, content_type='application/pdf')


# ── Trainers ──────────────────────────────────────────────────────────────────

class TrainerListCreate(generics.ListCreateAPIView):
    queryset = Trainer.objects.prefetch_related('sport_types').all()
    serializer_class = TrainerSerializer


class TrainerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trainer.objects.all()
    serializer_class = TrainerSerializer
    http_method_names = ['get', 'patch', 'delete']


# ── Sport Types ───────────────────────────────────────────────────────────────

class SportTypeListCreate(generics.ListCreateAPIView):
    queryset = SportType.objects.all()
    serializer_class = SportTypeSerializer


class SportTypeDelete(generics.DestroyAPIView):
    queryset = SportType.objects.all()
    serializer_class = SportTypeSerializer


# ── Schedule ──────────────────────────────────────────────────────────────────

class ScheduleListCreate(generics.ListCreateAPIView):
    queryset = Schedule.objects.select_related('trainer', 'sport_type').all()
    serializer_class = ScheduleSerializer


# ── Payments ──────────────────────────────────────────────────────────────────

class PaymentListCreate(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related('member', 'sport_type').all()
    serializer_class = PaymentSerializer


# ── Notifications ─────────────────────────────────────────────────────────────

class NotificationListCreate(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


# ── Products ──────────────────────────────────────────────────────────────────

class ProductListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# ── File Upload ───────────────────────────────────────────────────────────────

import os
from django.conf import settings
from django.core.files.storage import default_storage


@api_view(['POST'])
def upload_image(request, model_type):
    file = request.FILES.get('image')
    if not file:
        return Response({'error': 'No file uploaded'}, status=400)

    ext = os.path.splitext(file.name)[1]
    filename = f"{int(timezone.now().timestamp())}{ext}"
    path = default_storage.save(f'Images/{filename}', file)
    url = f"{settings.BASE_URL}/Images/{filename}"

    model_map = {
        'member': (Member, 'cin', 'profile_pic'),
        'trainer': (Trainer, 'cin', 'profile_pic'),
        'sportType': (SportType, 'name', 'sport_pic'),
        'products': (Product, 'product_name', 'profile_pic'),
    }

    if model_type not in model_map:
        return Response({'error': 'Invalid type'}, status=400)

    Model, lookup_field, pic_field = model_map[model_type]
    identifier_key = 'imageid' if model_type != 'sportType' else 'fileName'
    identifier_key = 'productName' if model_type == 'products' else identifier_key
    identifier = request.data.get(identifier_key) or request.data.get('imageid')

    Model.objects.filter(**{lookup_field: identifier}).update(**{pic_field: url})
    return Response({'url': url})


# ── Dashboard ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
def dashboard(request):
    today = timezone.now()
    day = today.weekday()  # 0=Monday ... 6=Sunday
    month_ago = today - timezone.timedelta(days=30)

    members_count = Member.objects.count()
    trainers_count = Trainer.objects.count()
    unpaid_count = Payment.objects.filter(credit__gt=0).count()
    members_per_month = Member.objects.filter(created_at__gte=month_ago).count()

    total_income = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Monthly subscriptions table (index 1-12)
    table = [0] * 13
    monthly = Member.objects.extra(select={'month': "strftime('%%m', created_at)"}).values('month').annotate(count=Count('id'))
    for row in monthly:
        if row['month']:
            table[int(row['month'])] = row['count']

    # Sports income
    sports_income = Payment.objects.values('sport_type').annotate(income=Sum('amount'))
    sports_income_data = []
    for item in sports_income:
        sport = SportType.objects.filter(pk=item['sport_type']).first()
        sports_income_data.append({'sport': SportTypeSerializer(sport).data if sport else None, 'income': item['income']})

    # Sports by members
    sports_members = Payment.objects.values('sport_type').annotate(count=Count('id'))
    sports_members_data = []
    for item in sports_members:
        sport = SportType.objects.filter(pk=item['sport_type']).first()
        sports_members_data.append({'sport': SportTypeSerializer(sport).data if sport else None, 'members': item['count']})

    # Today's schedule
    today_schedule = Schedule.objects.filter(days_of_week__contains=day)
    notifications = Notification.objects.all()

    return Response({
        'membersCount': members_count,
        'trainersCount': trainers_count,
        'totalIncome': total_income,
        'membersPerMonth': members_per_month,
        'unpaidCount': unpaid_count,
        'table': table,
        'sportTypesByIncome': sports_income_data,
        'todaySchedule': ScheduleSerializer(today_schedule, many=True).data,
        'sportsByMembers': sports_members_data,
        'notifications': NotificationSerializer(notifications, many=True).data,
    })
