from rest_framework import serializers

from photocards.models import PhotoCard, Group, Artist


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class ArtistSerializer(serializers.ModelSerializer):
    group = GroupSerializer()

    class Meta:
        model = Artist
        fields = '__all__'


class PhotoCardSerializer(serializers.ModelSerializer):
    artist_set = ArtistSerializer(many=True)

    class Meta:
        model = PhotoCard
        fields = '__all__'
