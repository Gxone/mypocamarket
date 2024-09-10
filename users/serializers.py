from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']

    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data['name'],
            email=validated_data['email'],
            password=validated_data['password'],
            birth=validated_data.get('birth', None),
            gender=validated_data.get('gender', None)
        )
        return user
