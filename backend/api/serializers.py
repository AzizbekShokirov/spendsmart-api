from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import User, Transaction, Account, Bill, Expense, Goal, MainGoal


class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        # fields = ['id', 'username', 'email', 'password', 'password_confirmation']
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}}
        }

    def validate(self, data):
        # Validate password strength
        validate_password(data["password"])

        # Validate email uniqueness
        if User.objects.filter(email=data["email"]).exists():
            raise ValidationError({"email": "A user with that email already exists."})

        # Validate username uniqueness
        if User.objects.filter(username=data["username"]).exists():
            raise ValidationError(
                {"username": "A username with that name already exists."}
            )

        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, data):
        # Attempt to authenticate the user directly without checking existence separately
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            # Raise a general error without specifying if the username or password was incorrect
            raise ValidationError("Invalid username or password.", code="authorization")
        # If authentication is successful, include the user object in the validated data
        data["user"] = user
        return data


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "phone_number",
            "photo",
        ]
        read_only_fields = ["id", "username", "email", "date_joined"]

    def validate(self, data):
        if data.get("phone_number") and not data["phone_number"].isdigit():
            raise ValidationError(
                {"phone_number": "Phone number must contain only digits."}
            )
        if data.get("phone_number") and len(data["phone_number"]) > 15:
            raise ValidationError(
                {"phone_number": "Phone number must be less than 15 characters."}
            )
        return data


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={"input_type": "password"})
    new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, data):
        # Validate new password strength
        validate_password(data["new_password"])
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        if not User.objects.filter(email=data["email"]).exists():
            raise ValidationError({"email": "A user with that email does not exist."})
        return data


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    # Custom date and time formatting
    date = serializers.DateTimeField(format="%d-%m-%Y")
    time = serializers.DateTimeField(format="%H:%M:%S", source="date")

    class Meta:
        model = Transaction
        fields = ["id", "title", "amount", "date", "time", "shop_name", "user"]

    def validate(self, data):
        # Validate user
        if data["user"] != self.context["request"].user:
            raise serializers.ValidationError(
                {"user": "You can only create transactions for yourself."}
            )

        # Validate title
        if not data.get("title"):
            raise serializers.ValidationError({"title": "Title cannot be empty."})

        # Validate date
        if data["date"] > timezone.now():
            raise serializers.ValidationError(
                {"date": "You cannot create transactions in the future."}
            )

        # Validate amount
        if data["amount"] < 0:
            raise serializers.ValidationError(
                {"amount": "Amount must be a positive number."}
            )

        return data


class AccountSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Account
        fields = [
            "id",
            "account_type",
            "account_number",
            "balance",
            "organization_name",
            "user",
        ]

    def validate(self, data):
        # Validate user
        if data["user"] != self.context["request"].user:
            raise serializers.ValidationError(
                {"user": "You can only create accounts for yourself."}
            )

        # Validate account number
        if not data.get("account_number"):
            raise serializers.ValidationError(
                {"account_number": "Account number cannot be empty."}
            )

        # Validate balance
        if data["balance"] < 0:
            raise serializers.ValidationError(
                {"balance": "Balance must be a positive number."}
            )

        # Validate organization name
        if not data.get("organization_name"):
            raise serializers.ValidationError(
                {"organization_name": "Organization name cannot be empty."}
            )

        return data


class BillSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Bill
        fields = [
            "id",
            "title",
            "description",
            "due_date",
            "amount",
            "recurring",
            "user",
        ]

    def validate(self, data):
        # Validate user
        if data["user"] != self.context["request"].user:
            raise serializers.ValidationError(
                {"user": "You can only create bills for yourself."}
            )

        # Validate title
        if not data.get("title"):
            raise serializers.ValidationError({"title": "Title cannot be empty."})

        # Validate due date
        if data["due_date"] < timezone.now().date():
            raise serializers.ValidationError(
                {"due_date": "Due date cannot be in the past."}
            )

        # Validate amount
        if data["amount"] < 0:
            raise serializers.ValidationError(
                {"amount": "Amount must be a positive number."}
            )

        return data


class ExpenseSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Expense
        fields = ["id", "category", "title", "amount", "date", "user"]

    def validate(self, data):
        # Validate user
        if data["user"] != self.context["request"].user:
            raise serializers.ValidationError(
                {"user": "You can only create expenses for yourself."}
            )

        # Validate title
        if not data.get("title"):
            raise serializers.ValidationError({"title": "Title cannot be empty."})

        # Validate date
        if data["date"] > timezone.now().date():
            raise serializers.ValidationError({"date": "Date cannot be in the future."})

        # Validate amount
        if data["amount"] < 0:
            raise serializers.ValidationError(
                {"amount": "Amount must be a positive number."}
            )

        return data


class GoalSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = [
            "id",
            "category",
            "target_amount",
            "achieved_amount",
            "start_date",
            "end_date",
            "user",
        ]

    def validate(self, data):
        # Validate user
        if data["user"] != self.context["request"].user:
            raise serializers.ValidationError(
                {"user": "You can only create expenses for yourself."}
            )

        # Validate start date
        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError(
                "The start date cannot be after the end date."
            )

        # Validate achieved amount
        if data.get("achieved_amount", 0) > data["target_amount"]:
            raise serializers.ValidationError(
                "Achieved amount cannot exceed the target amount."
            )

        return data


class MainGoalSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MainGoal
        fields = [
            "id",
            "target_amount",
            "achieved_amount",
            "start_date",
            "end_date",
            "user",
        ]

    def validate(self, data):
        # Validate user
        if data["user"] != self.context["request"].user:
            raise serializers.ValidationError(
                {"user": "You can only create expenses for yourself."}
            )

        # Validate start date
        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError(
                "The start date cannot be after the end date."
            )

        # Validate achieved amount
        if data.get("achieved_amount", 0) > data["target_amount"]:
            raise serializers.ValidationError(
                "Achieved amount cannot exceed the target amount."
            )

        return data
