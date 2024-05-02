import smtplib
from rest_framework import serializers
from authentication.models import Account, UserSignupEmailSenderModel
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_decode
from authentication.token import account_activation_token
from django.utils.encoding import force_str
from authentication.utils import sent_user_verify_email


class EmptySerializer(serializers.Serializer):
    pass


class SignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField()

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password']

    def validate(self, attrs):
        user = Account.objects.filter(email=attrs['email']).exists()
        if user:
            raise serializers.ValidationError({'email': 'User already exists with this email'})

        if len(attrs['first_name'].strip()) < 1:
            raise serializers.ValidationError({"first_name": "First name is required."})

        if len(attrs['last_name'].strip()) < 1:
            raise serializers.ValidationError({"last_name": "Last name is required."})

        if len(attrs['password']) < 8:
            raise serializers.ValidationError({"password": "Password must be more than 8 characters."})

        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        user = Account.objects.create(
            email=validated_data['email'],
            is_active=False,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        try:
            sent_user_verify_email(user)
        except smtplib.SMTPException as e:
            user.delete()
            return Response({'message': 'Internal Server Error.'})
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        try:
            user = Account.objects.get(email=attrs['email'], is_active=True)
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError({'password': 'Email or password is incorrect'})
        except Exception:
            raise serializers.ValidationError({"password": "Email or password is incorrect"})
        return attrs


class UserSignupEmailSenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSignupEmailSenderModel
        fields = '__all__'


class UserSignupEmailConfirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSignupEmailSenderModel
        fields = ['uid', 'token']

    def validate(self, attrs):
        if attrs['uid'] is not None and attrs['token'] is not None:
            email_user = UserSignupEmailSenderModel.objects.filter(uid=attrs['uid'], token=attrs['token']).exists()

            if not email_user:
                raise serializers.ValidationError({'non_field_errors': ['Token or uid is invalid!']})

            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = Account.objects.get(pk=uid)

            token_verified = account_activation_token.check_token(user, attrs['token'])

            if not token_verified:
                raise serializers.ValidationError({'non_field_errors': ['Invalid token!']})

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'first_name', 'last_name', 'email', 'profile_picture']
