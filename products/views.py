import os
import uuid
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
from celery.result import AsyncResult
from .models import Product
from .serializers import ProductSerializer
from processor.tasks import generate_mockup_task

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class MockupRequestView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        product_view_id = request.data.get('product_view_id')
        user_image = request.data.get('user_image')
        
        # Affine transform parameters
        scale_x = float(request.data.get('scale_x', 1.0))
        scale_y = float(request.data.get('scale_y', 1.0))
        rotation = float(request.data.get('rotation', 0.0))
        offset_x = float(request.data.get('offset_x', 0.0))
        offset_y = float(request.data.get('offset_y', 0.0))

        if not product_view_id or not user_image:
            return Response({'error': 'product_view_id and user_image are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Save uploaded image temporarily
        file_ext = os.path.splitext(user_image.name)[1]
        temp_filename = f"temp_user_img_{uuid.uuid4().hex}{file_ext}"
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_uploads', temp_filename)
        
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        path = default_storage.save(temp_path, user_image)

        # Dispatch Celery task
        task = generate_mockup_task.delay(product_view_id, path, scale_x, scale_y, rotation, offset_x, offset_y)

        return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)

class MockupStatusView(APIView):
    def get(self, request, task_id, *args, **kwargs):
        task_result = AsyncResult(task_id)
        result = {
            'task_id': task_id,
            'task_status': task_result.status,
            'task_result': task_result.result
        }
        return Response(result)
