import logging
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from apps.user.models import User
from apps.user.serializers import (
	UserSerializer, LoginSerializer, SignupSerializer
)
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

class UserView(ListAPIView):
	queryset = User.objects.all().order_by('first_name')
	serializer_class = UserSerializer
	pagination_class = LimitOffsetPagination

	def get_queryset(self):
		excludeUsersArr = []
		try:
			excludeUsers = self.request.query_params.get('exclude')
			if excludeUsers:
				userIds = excludeUsers.split(',')
				for userId in userIds:
					excludeUsersArr.append(int(userId))
		except:
			return []
		return super().get_queryset().exclude(id__in=excludeUsersArr)

class LoginApiView(TokenObtainPairView):
	permission_classes = [AllowAny]
	serializer_class = LoginSerializer

class SignupApiView(CreateAPIView):
	permission_classes = [AllowAny]
	queryset = User.objects.all()
	serializer_class = SignupSerializer

	def create(self, request, *args, **kwargs):
		logger.info("Received signup request")
		logger.debug(f"Request data: {request.data}")
		
		serializer = self.get_serializer(data=request.data)
		if not serializer.is_valid():
			logger.error(f"Validation errors: {serializer.errors}")
			return Response(
				serializer.errors,
				status=status.HTTP_400_BAD_REQUEST
			)
		
		try:
			self.perform_create(serializer)
			logger.info("User created successfully")
			return Response(
				serializer.data,
				status=status.HTTP_201_CREATED
			)
		except Exception as e:
			logger.error(f"Error during signup: {str(e)}")
			return Response(
				{"error": str(e)},
				status=status.HTTP_400_BAD_REQUEST
			)
