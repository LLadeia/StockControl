from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Product, ProductionLog, ProductRawMaterial, RawMaterial


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_superuser', 'is_staff', 'first_name', 'last_name']

class RawMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterial
        fields = ['id', 'name', 'stock', 'price', 'image']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'image']

class ProductRawMaterialSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    raw_material_name = serializers.CharField(source='raw_material.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price', max_digits=10, decimal_places=2, read_only=True
    )
    raw_material_price = serializers.DecimalField(
        source='raw_material.price', max_digits=10, decimal_places=2, read_only=True
    )
    manufacturing_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    cost = serializers.SerializerMethodField()

    class Meta:
        model = ProductRawMaterial
        fields = [
            'id',
            'product',
            'product_name',
            'product_price',
            'raw_material',
            'raw_material_name',
            'raw_material_price',
            'quantity',
            'price',
            'manufacturing_price',
            'cost',
        ]

    def get_cost(self, obj):
        try:
            qty = float(obj.quantity or 0)
            raw_price = float(getattr(obj.raw_material, 'price', 0) or 0)
            manuf = float(getattr(obj, 'manufacturing_price', 0) or 0)
            return qty * raw_price + manuf
        except Exception:
            return 0


class HistorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    model = serializers.CharField()
    object_id = serializers.IntegerField()
    object_str = serializers.CharField()
    changed_by = serializers.CharField()
    changed_at = serializers.DateTimeField()
    change_reason = serializers.CharField()
    changes = serializers.JSONField()

class ProductionLogSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductionLog
        fields = [
            'id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price', 'created_at'
        ]
