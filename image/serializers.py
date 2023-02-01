from .dmodels import Image
from rest_framework import serializers

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Image
        fields = ("caption", "image", "title")