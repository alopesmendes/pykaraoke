from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from domain.karaoke.exceptions import InvalidCredentials, InvalidParticipantData, PseudoTaken
from interface.api.karaoke.serializers import (
    ErrorSerializer,
    SignInRequestSerializer,
    SignUpRequestSerializer,
    SignUpResponseSerializer,
    TokenPairSerializer,
)
from pykaraoke import composition

NO_STORE = {"Cache-Control": "no-store"}


class SignUpView(APIView):
    authentication_classes: list = []
    permission_classes: list = [AllowAny]

    @extend_schema(
        request=SignUpRequestSerializer,
        responses={201: SignUpResponseSerializer, 400: ErrorSerializer, 409: ErrorSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = SignUpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = composition.sign_up(**serializer.validated_data)
        except InvalidParticipantData:
            return Response(
                {"detail": _("Invalid fullname or pseudo")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PseudoTaken:
            return Response(
                {"detail": _("That pseudo is already taken")},
                status=status.HTTP_409_CONFLICT,
            )
        body = {
            "participant_id": result.participant.id,
            "pseudo": result.participant.pseudo,
            "recovery_code": result.recovery_code,
            "access_token": result.tokens.access_token,
            "refresh_token": result.tokens.refresh_token,
        }
        return Response(body, status=status.HTTP_201_CREATED, headers=NO_STORE)


class SignInView(APIView):
    authentication_classes: list = []
    permission_classes: list = [AllowAny]

    @extend_schema(
        request=SignInRequestSerializer,
        responses={200: TokenPairSerializer, 401: ErrorSerializer},
    )
    def post(self, request: Request) -> Response:
        serializer = SignInRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = composition.sign_in(**serializer.validated_data)
        except InvalidCredentials:
            return Response(
                {"detail": _("Invalid credentials")},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        body = {
            "access_token": result.access_token,
            "refresh_token": result.refresh_token,
        }
        return Response(body, headers=NO_STORE)
