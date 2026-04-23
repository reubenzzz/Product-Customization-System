from rest_framework import serializers
from .models import Product, ProductView, PrintArea

class PrintAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintArea
        fields = '__all__'

class ProductViewSerializer(serializers.ModelSerializer):
    print_area = PrintAreaSerializer()

    class Meta:
        model = ProductView
        fields = ['id', 'name', 'base_image', 'print_area']

class ProductSerializer(serializers.ModelSerializer):
    views = ProductViewSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'views']
