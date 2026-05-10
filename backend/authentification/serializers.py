from rest_framework import serializers
from .models import Listing, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        # данные которые не возвращаются
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # удаление из кэша пороля
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class ListingSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.username", read_only=True)
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)

    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "description",
            "price",
            "city",
            "created_by",
            "created_by_id",
            "created_at",
        ]
