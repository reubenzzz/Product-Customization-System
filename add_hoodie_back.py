import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customization_engine.settings')
django.setup()

from products.models import Product, ProductView, PrintArea

def add_back():
    hoodie = Product.objects.get(name='Premium Hoodie')
    h_front = hoodie.views.first()
    h_p = h_front.print_area
    
    h_back, created = ProductView.objects.get_or_create(product=hoodie, name='Back', defaults={'base_image': h_front.base_image})
    print('Hoodie Back view added.')
    
    if created:
        PrintArea.objects.create(
            product_view=h_back, 
            top_left_x=h_p.top_left_x, top_left_y=h_p.top_left_y, 
            top_right_x=h_p.top_right_x, top_right_y=h_p.top_right_y, 
            bottom_right_x=h_p.bottom_right_x, bottom_right_y=h_p.bottom_right_y, 
            bottom_left_x=h_p.bottom_left_x, bottom_left_y=h_p.bottom_left_y
        )

if __name__ == '__main__':
    add_back()
