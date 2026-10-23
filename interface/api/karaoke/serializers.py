from rest_framework import serializers


class SignUpRequestSerializer(serializers.Serializer):
    fullname = serializers.CharField(required=True)
    pseudo = serializers.CharField(required=True)


class SignInRequestSerializer(serializers.Serializer):
    pseudo = serializers.CharField(required=True)
    recovery_code = serializers.CharField(required=True)


class TokenPairSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()


class SignUpResponseSerializer(serializers.Serializer):
    participant_id = serializers.UUIDField(required=True)
    pseudo = serializers.CharField(required=True)
    recovery_code = serializers.CharField(required=True)


class ErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()
