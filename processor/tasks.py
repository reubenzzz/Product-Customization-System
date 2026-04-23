import os
import uuid
from celery import shared_task
from django.conf import settings
from products.models import ProductView
from .engine import create_mockup

@shared_task
def generate_mockup_task(product_view_id, user_image_path, scale_x=1.0, scale_y=1.0, rotation=0.0, offset_x=0.0, offset_y=0.0):
    try:
        product_view = ProductView.objects.get(id=product_view_id)
        print_area = product_view.print_area
        product_name = product_view.product.name
        
        base_image_path = product_view.base_image.path
        
        # Ensure user_image_path is absolute
        if not os.path.isabs(user_image_path):
            user_image_path = os.path.join(settings.MEDIA_ROOT, user_image_path)
        
        print_area_coords = {
            'top_left': (print_area.top_left_x, print_area.top_left_y),
            'top_right': (print_area.top_right_x, print_area.top_right_y),
            'bottom_right': (print_area.bottom_right_x, print_area.bottom_right_y),
            'bottom_left': (print_area.bottom_left_x, print_area.bottom_left_y),
        }
        
        output_dir = os.path.join(settings.MEDIA_ROOT, 'mockups')
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = f"mockup_{uuid.uuid4().hex}.png"
        output_path = os.path.join(output_dir, output_filename)
        
        create_mockup(base_image_path, user_image_path, print_area_coords, output_path, product_name, scale_x, scale_y, rotation, offset_x, offset_y)
        
        output_url = os.path.join(settings.MEDIA_URL, 'mockups', output_filename).replace('\\', '/')
        return {'status': 'success', 'url': output_url}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
