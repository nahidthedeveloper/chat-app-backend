from datetime import datetime
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from authentication.models import Account, UserSignupEmailSenderModel
from authentication.serializer import SignupSerializer, LoginSerializer, UserSignupEmailConfirmSerializer, \
    EmptySerializer, ProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationViewSet(viewsets.ModelViewSet):
    serializer_class = SignupSerializer
    queryset = []

    def get_serializer_class(self):
        if self.action == 'signup':
            return SignupSerializer
        elif self.action == 'verify':
            return UserSignupEmailConfirmSerializer
        elif self.action == 'login':
            return LoginSerializer
        return EmptySerializer

    def list(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], url_path='signup')
    def signup(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'Please confirm your email address to complete the registration'})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'], url_path='verify')
    def verify(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user_id = force_str(urlsafe_base64_decode(serializer.data['uid']))

            user = Account.objects.get(pk=user_id)
            user.is_active = True
            user.save()

            get_user_data = UserSignupEmailSenderModel.objects.filter(uid=serializer.data['uid'])
            get_user_data.delete()

            return Response({'message': 'Your account has been activated successfully.'}, status=status.HTTP_200_OK)
        return Response({'non_field_errors': ['Activation link is invalid!']},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['POST'], url_path='login')
    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = Account.objects.get(email=serializer.data['email'])
            user.last_login = datetime.now()
            user.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'token': str(refresh.access_token),
                'email': user.email,
                'user_id': user.id,

            })
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(pk=user.pk)
