from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Product, ProductionLog, ProductRawMaterial, RawMaterial
from .serializers import (
    ProductionLogSerializer,
    ProductRawMaterialSerializer,
    ProductSerializer,
    RawMaterialSerializer,
    UserSerializer,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    """Endpoint para retornar informações do usuário autenticado"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class RawMaterialViewSet(ModelViewSet):
    queryset = RawMaterial.objects.all()
    serializer_class = RawMaterialSerializer
    permission_classes = [IsAuthenticated]



class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def can_produce(self, request, pk=None):
        product = self.get_object()
        relations = ProductRawMaterial.objects.filter(product=product)

        for relation in relations:
            raw_material = relation.raw_material
            required = relation.quantity

            if raw_material.stock < required:
                return Response(
                    {
                        "can_produce": False,
                        "limiting_raw_material": raw_material.name,
                        "required": required,
                        "available": raw_material.stock
                    },
                    status=status.HTTP_200_OK
                )

        return Response({"can_produce": True})

    @action(detail=True, methods=['post'])
    def produce(self, request, pk=None):
        product = self.get_object()
        quantity = int(request.data.get("quantity", 1))

        relations = ProductRawMaterial.objects.filter(product=product)

        for relation in relations:
            raw_material = relation.raw_material
            required = relation.quantity * quantity

            if raw_material.stock < required:
                return Response(
                    {
                        "success": False,
                        "raw_material": raw_material.name
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            for relation in relations:
                raw_material = relation.raw_material
                raw_material.stock -= relation.quantity * quantity
                raw_material.save()
            # Atualiza estoque do produto produzido
            try:
                product.stock = (product.stock or 0) + quantity
                product.save()
            except Exception:
                pass

            # Registra produção com preços (inclui material + manufacturing, sem produto)
            unit_price = 0
            for relation in relations:
                raw_material_cost = relation.quantity * float(relation.raw_material.price or 0)
                manufacturing_cost = float(relation.manufacturing_price or 0)
                unit_price += raw_material_cost + manufacturing_cost
            total_price = unit_price * quantity
            ProductionLog.objects.create(
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
            )

        return Response({"success": True})



class ProductRawMaterialViewSet(ModelViewSet):
    queryset = ProductRawMaterial.objects.all()
    serializer_class = ProductRawMaterialSerializer
    permission_classes = [IsAuthenticated]


class ProductionLogViewSet(ModelViewSet):
    queryset = ProductionLog.objects.all()
    serializer_class = ProductionLogSerializer
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated]


    @action(detail=False, methods=['get'])
    def by_model(self, request):
        """Retorna histórico filtrado por modelo"""
        model_type = request.query_params.get('model', '')

        if model_type == 'Product':
            histories = Product.history.all().order_by('-history_date')
        elif model_type == 'RawMaterial':
            histories = RawMaterial.history.all().order_by('-history_date')
        elif model_type == 'ProductRawMaterial':
            histories = ProductRawMaterial.history.all().order_by('-history_date')
        else:
            return Response({"error": "Model não especificado"}, status=400)

        changes = []
        for history in histories:
            changes.append({
                "id": history.id,
                "object_str": str(history),
                "changed_by": history.history_user.username if history.history_user else "Sistema",
                "changed_at": history.history_date,
                "change_reason": history.get_history_type_display(),
            })

        return Response(changes)
