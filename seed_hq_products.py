import os
import django
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customization_engine.settings')
django.setup()

from products.models import Product, ProductView, PrintArea
from django.core.files.base import ContentFile
from django.conf import settings

def seed_db():
    # Clear existing data
    Product.objects.all().delete()
    print("Deleted existing products.")

    products_data = [
        {
            'name': 'Ceramic Coffee Mug',
            'image_path': os.path.join(settings.BASE_DIR, 'media', 'products', 'base_images', 'hq_mug.png'),
            'filename': 'hq_mug.png',
            'print_area': {'tl_x': 300, 'tl_y': 300, 'tr_x': 700, 'tr_y': 300, 'br_x': 700, 'br_y': 700, 'bl_x': 300, 'bl_y': 700}
        },
        {
            'name': 'Premium Hoodie',
            'image_path': os.path.join(settings.BASE_DIR, 'media', 'products', 'base_images', 'hq_hoodie.png'),
            'filename': 'hq_hoodie.png',
            'print_area': {'tl_x': 350, 'tl_y': 300, 'tr_x': 650, 'tr_y': 300, 'br_x': 650, 'br_y': 600, 'bl_x': 350, 'bl_y': 600}
        },
        {
            'name': 'Classic T-Shirt',
            'image_path': os.path.join(settings.BASE_DIR, 'media', 'products', 'base_images', 'hq_tshirt.png'),
            'filename': 'hq_tshirt.png',
            'print_area': {'tl_x': 350, 'tl_y': 300, 'tr_x': 650, 'tr_y': 300, 'br_x': 650, 'br_y': 600, 'bl_x': 350, 'bl_y': 600}
        },
        {
            'name': 'Baseball Cap',
            'image_path': os.path.join(settings.BASE_DIR, 'media', 'products', 'base_images', 'hq_cap.png'),
            'filename': 'hq_cap.png',
            'print_area': {'tl_x': 400, 'tl_y': 400, 'tr_x': 600, 'tr_y': 400, 'br_x': 600, 'br_y': 500, 'bl_x': 400, 'bl_y': 500}
        }
    ]

    for item in products_data:
        product = Product.objects.create(name=item['name'])
        view = ProductView(product=product, name='Front')
        
        with open(item['image_path'], 'rb') as f:
            view.base_image.save(item['filename'], ContentFile(f.read()), save=True)
            
        coords = item['print_area']
        PrintArea.objects.create(
            product_view=view,
            top_left_x=coords['tl_x'],
            top_left_y=coords['tl_y'],
            top_right_x=coords['tr_x'],
            top_right_y=coords['tr_y'],
            bottom_right_x=coords['br_x'],
            bottom_right_y=coords['br_y'],
            bottom_left_x=coords['bl_x'],
            bottom_left_y=coords['bl_y']
        )
        print(f"Created {item['name']}")

if __name__ == '__main__':
    seed_db()
