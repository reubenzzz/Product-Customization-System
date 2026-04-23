import os
import django
import cv2
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customization_engine.settings')
django.setup()

from products.models import Product, ProductView, PrintArea
from django.core.files.base import ContentFile

def process_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Image not found!")
        return

    # Convert to grayscale to find individual products
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Find contours for products
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    product_idx = 1
    
    # Make sure media dirs exist
    os.makedirs('media/products/base_images', exist_ok=True)
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w < 100 or h < 100:  # Ignore small noise
            continue
            
        # Add padding
        pad = 20
        y1 = max(0, y - pad)
        y2 = min(img.shape[0], y + h + pad)
        x1 = max(0, x - pad)
        x2 = min(img.shape[1], x + w + pad)
        
        roi = img[y1:y2, x1:x2].copy()
        
        # Find red rectangles in this ROI
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Red ranges
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        
        # Dilate mask slightly to cover the whole red line
        kernel = np.ones((5,5), np.uint8)
        red_mask = cv2.dilate(red_mask, kernel, iterations=1)
        
        # Find contours of the red box
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not red_contours:
            continue
            
        # Get largest red contour
        red_cnt = max(red_contours, key=cv2.contourArea)
        rx, ry, rw, rh = cv2.boundingRect(red_cnt)
        
        if rw < 10 or rh < 10:
            continue
            
        # Inpaint the red lines so they don't show through the mockup
        roi_clean = cv2.inpaint(roi, red_mask, 3, cv2.INPAINT_TELEA)
        
        # Save the clean image
        filename = f"product_auto_{product_idx}.jpg"
        filepath = os.path.join('media/products/base_images', filename)
        cv2.imwrite(filepath, roi_clean)
        
        # Database operations
        product = Product.objects.create(name=f"Auto Product {product_idx}")
        
        view = ProductView(product=product, name="Default View")
        with open(filepath, 'rb') as f:
            view.base_image.save(filename, ContentFile(f.read()), save=True)
            
        # Create PrintArea
        PrintArea.objects.create(
            product_view=view,
            top_left_x=rx,
            top_left_y=ry,
            top_right_x=rx + rw,
            top_right_y=ry,
            bottom_right_x=rx + rw,
            bottom_right_y=ry + rh,
            bottom_left_x=rx,
            bottom_left_y=ry + rh
        )
        
        print(f"Created Product {product_idx} with print area {rw}x{rh}")
        product_idx += 1

if __name__ == "__main__":
    # Clear existing data for a clean slate
    Product.objects.all().delete()
    print("Deleted existing products.")
    process_image('download.jpg')
    print("Database seeding complete!")
