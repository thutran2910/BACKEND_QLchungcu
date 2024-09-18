from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from .models import Resident, Flat, Bill, Item, Feedback, Survey, FaMember, SurveyResult, Product, Cart, \
    CartProduct, OrderProduct, Order

class BillSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='resident.first_name', read_only=True)
    last_name = serializers.CharField(source='resident.last_name', read_only=True)
    phone = serializers.CharField(source='resident.phone', read_only=True)
    resident_id = serializers.PrimaryKeyRelatedField(queryset=Resident.objects.all(), write_only=True, source='resident')
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False)
    avatar_url = serializers.SerializerMethodField()

    def get_image_url(self, instance):
        if instance.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(instance.image.url)
            return instance.image.url
        return None
    def get_avatar_url(self, instance):
        if instance.resident.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(instance.resident.avatar.url)
            return instance.resident.avatar.url
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image_url'] = self.get_image_url(instance)
        rep['avatar_url'] = self.get_avatar_url(instance)
        return rep
    class Meta:
        model = Bill
        fields = '__all__'



class SurveySerializer(ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'

class SurveyResultSerializer(ModelSerializer):
    class Meta:
        model = SurveyResult
        fields = '__all__'
