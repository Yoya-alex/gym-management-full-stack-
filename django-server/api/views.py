import os
from django.contrib.auth import authenticate
from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import HttpResponse

from .models import User, Member, Trainer, SportType, Schedule, Payment, Notification, Product, Enrollment
from .serializers import (
    UserSerializer, RegisterSerializer, MemberSerializer, TrainerSerializer,
    SportTypeSerializer, ScheduleSerializer, PaymentSerializer,
    NotificationSerializer, ProductSerializer, EnrollmentSerializer
)
from .permissions import IsAdmin
from .utils import generate_member_card_pdf, generate_invoice_pdf


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


# ── User Profile (Normal User) ────────────────────────────────────────────────

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    """Get or update the logged-in user's member profile."""
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        if request.method == 'GET':
            return Response({'message': 'Profile not found. Please complete your profile.'}, status=404)
        member = None

    if request.method == 'GET':
        return Response(MemberSerializer(member).data)

    if request.method == 'PUT':
        if member:
            serializer = MemberSerializer(member, data=request.data, partial=True)
        else:
            data = request.data.copy()
            serializer = MemberSerializer(data=data)
        if serializer.is_valid():
            obj = serializer.save()
            if not member:
                obj.user = request.user
                obj.save()
            return Response(MemberSerializer(obj).data)
        return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_schedule(request):
    """Get schedules for the logged-in user's sport type."""
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return Response([])
    schedules = Schedule.objects.filter(sport_type=member.sport_type).select_related('trainer', 'sport_type')
    return Response(ScheduleSerializer(schedules, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_payments(request):
    """Get payment history for the logged-in user."""
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return Response([])
    payments = Payment.objects.filter(member=member).select_related('sport_type', 'member').order_by('-date')
    return Response(PaymentSerializer(payments, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_notifications(request):
    """Get notifications for the logged-in user."""
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return Response([])
    notifications = Notification.objects.filter(member=member).order_by('-created_at')
    return Response(NotificationSerializer(notifications, many=True).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    notif = Notification.objects.filter(pk=pk).first()
    if not notif:
        return Response({'message': 'Not found'}, status=404)
    notif.is_unread = False
    notif.save()
    return Response({'message': 'Marked as read'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_card(request):
    """Generate membership card PDF for the logged-in user."""
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return Response({'message': 'Profile not found'}, status=404)
    pdf = generate_member_card_pdf(member)
    return HttpResponse(pdf, content_type='application/pdf')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_membership_status(request):
    """Returns the full membership status for the logged-in user."""
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return Response({'message': 'Profile not found'}, status=404)

    today = timezone.now().date()
    last_payment = Payment.objects.filter(member=member).order_by('-date').first()

    is_active = False
    days_remaining = 0
    if member.membership_end:
        is_active = member.membership_end >= today
        days_remaining = (member.membership_end - today).days if is_active else 0

    return Response({
        'has_paid': member.has_paid,
        'membership_active': is_active,
        'membership_start': member.membership_start,
        'membership_end': member.membership_end,
        'days_remaining': days_remaining,
        'sport_type': member.sport_type.name if member.sport_type else None,
        'trainer': f"{member.trainer.first_name} {member.trainer.last_name}" if member.trainer else None,
        'last_payment': {
            'amount': last_payment.amount,
            'date': last_payment.date,
            'months': last_payment.months,
            'payment_type': last_payment.payment_type,
            'status': last_payment.status,
        } if last_payment else None,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_enrollments(request):
    """Get class enrollments for the logged-in user."""
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return Response([])
    enrollments = Enrollment.objects.filter(member=member).select_related('schedule')
    return Response(EnrollmentSerializer(enrollments, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_class(request):
    """Enroll logged-in user in a class."""
    try:
        member = request.user.member_profile
    except Member.DoesNotExist:
        return Response({'message': 'Complete your profile first'}, status=400)
    schedule_id = request.data.get('schedule_id')
    schedule = Schedule.objects.filter(pk=schedule_id).first()
    if not schedule:
        return Response({'message': 'Class not found'}, status=404)
    if schedule.is_full:
        return Response({'message': 'Class is full'}, status=400)
    enrollment, created = Enrollment.objects.get_or_create(member=member, schedule=schedule)
    if not created:
        return Response({'message': 'Already enrolled'}, status=400)
    schedule.enrolled_count += 1
    schedule.save()
    # Notify user
    Notification.objects.create(
        member=member,
        type='enrollment',
        title='Class Enrollment Confirmed',
        description=f'You have been enrolled in {schedule.title}.',
        is_unread=True,
    )
    return Response({'message': 'Enrolled successfully'})


# ── Members (Admin) ───────────────────────────────────────────────────────────

class MemberListCreate(generics.ListCreateAPIView):
    queryset = Member.objects.select_related('trainer', 'sport_type').all()
    serializer_class = MemberSerializer


class MemberDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    http_method_names = ['get', 'patch', 'delete']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def member_card(request, pk):
    member = Member.objects.filter(pk=pk).first()
    if not member:
        return Response({'error': 'Not found'}, status=404)
    pdf = generate_member_card_pdf(member)
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


class SportTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SportType.objects.all()
    serializer_class = SportTypeSerializer


# ── Schedule ──────────────────────────────────────────────────────────────────

class ScheduleListCreate(generics.ListCreateAPIView):
    queryset = Schedule.objects.select_related('trainer', 'sport_type').all()
    serializer_class = ScheduleSerializer


class ScheduleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    http_method_names = ['get', 'patch', 'delete']


# ── Payments ──────────────────────────────────────────────────────────────────

class PaymentListCreate(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related('member', 'sport_type').all()
    serializer_class = PaymentSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_invoice(request, pk):
    payment = Payment.objects.filter(pk=pk).select_related('member', 'sport_type').first()
    if not payment:
        return Response({'error': 'Not found'}, status=404)
    pdf = generate_invoice_pdf(payment)
    return HttpResponse(pdf, content_type='application/pdf')


# ── Notifications ─────────────────────────────────────────────────────────────

class NotificationListCreate(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


# ── Products ──────────────────────────────────────────────────────────────────

class ProductListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# ── Enrollments ───────────────────────────────────────────────────────────────

class EnrollmentListCreate(generics.ListCreateAPIView):
    queryset = Enrollment.objects.select_related('member', 'schedule').all()
    serializer_class = EnrollmentSerializer


# ── File Upload ───────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request, model_type):
    file = request.FILES.get('image')
    if not file:
        return Response({'error': 'No file uploaded'}, status=400)
    ext = os.path.splitext(file.name)[1]
    filename = f"{int(timezone.now().timestamp())}{ext}"
    default_storage.save(f'Images/{filename}', file)
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
    identifier_key = 'imageid' if model_type not in ('sportType', 'products') else ('fileName' if model_type == 'sportType' else 'productName')
    identifier = request.data.get(identifier_key) or request.data.get('imageid')
    Model.objects.filter(**{lookup_field: identifier}).update(**{pic_field: url})
    return Response({'url': url})


# ── Dashboard ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    today = timezone.now()
    day = today.weekday()
    month_ago = today - timezone.timedelta(days=30)

    members_count = Member.objects.count()
    trainers_count = Trainer.objects.count()
    unpaid_count = Payment.objects.filter(credit__gt=0).count()
    members_per_month = Member.objects.filter(created_at__gte=month_ago).count()
    active_subscriptions = Member.objects.filter(membership_end__gte=today.date()).count()
    total_income = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    table = [0] * 13
    monthly = Member.objects.extra(select={'month': "strftime('%%m', created_at)"}).values('month').annotate(count=Count('id'))
    for row in monthly:
        if row['month']:
            table[int(row['month'])] = row['count']

    sports_income = Payment.objects.values('sport_type').annotate(income=Sum('amount'))
    sports_income_data = []
    for item in sports_income:
        sport = SportType.objects.filter(pk=item['sport_type']).first()
        sports_income_data.append({'sport': SportTypeSerializer(sport).data if sport else None, 'income': item['income']})

    sports_members = Payment.objects.values('sport_type').annotate(count=Count('id'))
    sports_members_data = []
    for item in sports_members:
        sport = SportType.objects.filter(pk=item['sport_type']).first()
        sports_members_data.append({'sport': SportTypeSerializer(sport).data if sport else None, 'members': item['count']})

    today_schedule = Schedule.objects.filter(days_of_week__contains=day)
    notifications = Notification.objects.all().order_by('-created_at')[:10]

    return Response({
        'membersCount': members_count,
        'trainersCount': trainers_count,
        'totalIncome': total_income,
        'membersPerMonth': members_per_month,
        'unpaidCount': unpaid_count,
        'activeSubscriptions': active_subscriptions,
        'table': table,
        'sportTypesByIncome': sports_income_data,
        'todaySchedule': ScheduleSerializer(today_schedule, many=True).data,
        'sportsByMembers': sports_members_data,
        'notifications': NotificationSerializer(notifications, many=True).data,
    })
