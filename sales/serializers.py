from rest_framework import serializers

from photocards.serializers import PhotoCardSerializer
from sales.models import Sale


class SaleSerializer(serializers.ModelSerializer):
    photocard = PhotoCardSerializer()

    class Meta:
        model = Sale
        fields = ('id', 'photocard', 'price')


class SaleDetailSerializer(serializers.ModelSerializer):
    photocard = PhotoCardSerializer()

    class Meta:
        model = Sale
        fields = ('id', 'photocard', 'price', 'fee', 'total_price', 'recent_order_price_list')


class SaleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'

    def create(self, validated_data):
        sale = Sale.objects.create(
            state=validated_data.get('state', 1),  # (1, 판매 중)
            photocard=validated_data['photocard'],
            seller=validated_data['seller'],
            price=validated_data['price']
        )
        return sale
