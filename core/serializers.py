from rest_framework import serializers


class PersonSerializer(serializers.Serializer):
    image = serializers.ImageField()
    description = serializers.CharField(required=False, allow_blank=True)
