from .dmodels import Image
from rest_framework import serializers

class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField()
    caption = serializers.CharField(required=False, default=0)
    title = serializers.CharField(required=False, default=0)

    def create(self, validated_data):
        image = validated_data.get('image')
        validated_data.setdefault('caption', '')
        validated_data.setdefault('title', '')

        return Image.objects.create(**validated_data)