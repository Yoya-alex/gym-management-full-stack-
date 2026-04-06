from rest_framework import serializers
from .models import User, Member, Trainer, SportType, Schedule, Payment, Notification, Product, Enrollment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        role = validated_data.pop('role', 'moderator')
        user = User.objects.create_user(**validated_data)
        user.role = role
        user.save()
        return user


class SportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportType
        fields = '__all__'


class TrainerSerializer(serializers.ModelSerializer):
    sport_types = SportTypeSerializer(many=True, read_only=True)
    sport_type_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=SportType.objects.all(), write_only=True, source='sport_types'
    )

    class Meta:
        model = Trainer
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    trainer = TrainerSerializer(read_only=True)
    sport_type = SportTypeSerializer(read_only=True)
    trainer_id = serializers.PrimaryKeyRelatedField(
        queryset=Trainer.objects.all(), write_only=True, source='trainer', required=False, allow_null=True
    )
    sport_type_id = serializers.PrimaryKeyRelatedField(
        queryset=SportType.objects.all(), write_only=True, source='sport_type', required=False, allow_null=True
    )
    membership_active = serializers.ReadOnlyField()

    class Meta:
        model = Member
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    trainer = TrainerSerializer(read_only=True)
    sport_type = SportTypeSerializer(read_only=True)
    trainer_id = serializers.PrimaryKeyRelatedField(
        queryset=Trainer.objects.all(), write_only=True, source='trainer', required=False, allow_null=True
    )
    sport_type_id = serializers.PrimaryKeyRelatedField(
        queryset=SportType.objects.all(), write_only=True, source='sport_type', required=False, allow_null=True
    )
    is_full = serializers.ReadOnlyField()

    class Meta:
        model = Schedule
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(read_only=True)
    schedule_id = serializers.PrimaryKeyRelatedField(
        queryset=Schedule.objects.all(), write_only=True, source='schedule'
    )

    class Meta:
        model = Enrollment
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)
    sport_type = SportTypeSerializer(read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), write_only=True, source='member'
    )
    sport_type_id = serializers.PrimaryKeyRelatedField(
        queryset=SportType.objects.all(), write_only=True, source='sport_type', required=False, allow_null=True
    )

    class Meta:
        model = Payment
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
