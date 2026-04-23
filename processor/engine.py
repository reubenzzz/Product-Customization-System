import cv2
import numpy as np
import math

def apply_affine_transform(img, scale_x, scale_y, rotation_deg, offset_x, offset_y):
    h, w = img.shape[:2]
    center = (w / 2, h / 2)

    # Calculate rotation and scale matrix
    # Note: we need independent scale_x and scale_y, but getRotationMatrix2D does uniform scale.
    # So we do scaling manually first, then rotation and translation.
    
    # 1. Scale
    scaled_w = int(w * scale_x)
    scaled_h = int(h * scale_y)
    
    # Avoid zero dimension
    if scaled_w <= 0 or scaled_h <= 0:
        return img
        
    scaled_img = cv2.resize(img, (scaled_w, scaled_h), interpolation=cv2.INTER_LINEAR)
    
    # Pad or crop back to original size to maintain canvas
    canvas = np.zeros((h, w, img.shape[2]), dtype=img.dtype)
    
    # Calculate placement to center it
    x_offset = (w - scaled_w) // 2
    y_offset = (h - scaled_h) // 2
    
    # Paste scaled image onto canvas
    # Source bounds
    src_y1 = max(0, -y_offset)
    src_y2 = scaled_h - max(0, y_offset + scaled_h - h)
    src_x1 = max(0, -x_offset)
    src_x2 = scaled_w - max(0, x_offset + scaled_w - w)
    
    # Dest bounds
    dst_y1 = max(0, y_offset)
    dst_y2 = min(h, y_offset + scaled_h)
    dst_x1 = max(0, x_offset)
    dst_x2 = min(w, x_offset + scaled_w)
    
    if dst_y2 > dst_y1 and dst_x2 > dst_x1:
        canvas[dst_y1:dst_y2, dst_x1:dst_x2] = scaled_img[src_y1:src_y2, src_x1:src_x2]

    # 2. Rotation and Translation
    # offset_x/y from frontend are typically percentage or pixels. Let's assume pixels relative to original w/h
    M = cv2.getRotationMatrix2D(center, rotation_deg, 1.0)
    M[0, 2] += offset_x
    M[1, 2] += offset_y
    
    transformed = cv2.warpAffine(canvas, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    return transformed

def apply_cylindrical_warp(img):
    """
    Simulates wrapping the image around a cylinder (like a mug).
    """
    h, w = img.shape[:2]
    K = np.array([
        [w, 0, w/2],
        [0, h, h/2],
        [0, 0, 1]
    ], dtype=np.float32)

    # Cylinder radius
    r = w / 2.0
    
    # Create mesh
    y_i, x_i = np.indices((h, w), dtype=np.float32)
    
    # Map x to theta
    theta = (x_i - w/2) / r
    
    # Map theta to cylindrical coordinates
    x_c = r * np.sin(theta)
    y_c = y_i - h/2
    z_c = r * np.cos(theta)
    
    # Project back to 2D
    x_p = K[0,0] * (x_c / z_c) + K[0,2]
    y_p = K[1,1] * (y_c / z_c) + K[1,2]
    
    # Map coordinates
    map_x = np.float32(x_p)
    map_y = np.float32(y_p)
    
    warped = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    return warped

def create_mockup(base_image_path, user_image_path, print_area_coords, output_path, product_name="Unknown", scale_x=1.0, scale_y=1.0, rotation=0.0, offset_x=0.0, offset_y=0.0):
    # Load images
    base_img = cv2.imread(base_image_path)
    user_img = cv2.imread(user_image_path, cv2.IMREAD_UNCHANGED)
    
    if base_img is None or user_img is None:
        raise ValueError("Could not read base or user image.")
        
    # If user image doesn't have an alpha channel, add one
    if len(user_img.shape) == 2 or user_img.shape[2] == 3:
        if len(user_img.shape) == 2:
            user_img = cv2.cvtColor(user_img, cv2.COLOR_GRAY2BGRA)
        else:
            user_img = cv2.cvtColor(user_img, cv2.COLOR_BGR2BGRA)

    # 1. Apply frontend affine transformations (Scale, Rotate, Translate)
    user_img = apply_affine_transform(user_img, scale_x, scale_y, rotation, offset_x, offset_y)

    # 2. Apply Cylindrical warp if it's a mug
    if "Mug" in product_name:
        user_img = apply_cylindrical_warp(user_img)

    base_h, base_w = base_img.shape[:2]
    user_h, user_w = user_img.shape[:2]

    # 3. Perspective Alignment
    src_pts = np.array([[0, 0], [user_w - 1, 0], [user_w - 1, user_h - 1], [0, user_h - 1]], dtype="float32")
    dst_pts = np.array([
        print_area_coords['top_left'],
        print_area_coords['top_right'],
        print_area_coords['bottom_right'],
        print_area_coords['bottom_left']
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped_user_img = cv2.warpPerspective(user_img, M, (base_w, base_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))

    mask = warped_user_img[:, :, 3] / 255.0
    warped_color = warped_user_img[:, :, :3]

    # 4. Fabric Conformation (Displacement Mapping)
    gray_base = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)
    blurred_base = cv2.GaussianBlur(gray_base, (5, 5), 0)

    grad_x = cv2.Sobel(blurred_base, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(blurred_base, cv2.CV_32F, 0, 1, ksize=3)
    
    displacement_scale = 5.0
    grad_x = (grad_x / 255.0) * displacement_scale
    grad_y = (grad_y / 255.0) * displacement_scale

    x, y = np.meshgrid(np.arange(base_w), np.arange(base_h))
    map_x = np.float32(x + grad_x)
    map_y = np.float32(y + grad_y)

    displaced_color = cv2.remap(warped_color, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
    displaced_mask = cv2.remap(mask, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    # 5. Realistic Blending
    displaced_mask_3c = np.dstack([displaced_mask] * 3)
    
    base_float = base_img.astype(np.float32) / 255.0
    displaced_color_float = displaced_color.astype(np.float32) / 255.0

    # Boost contrast of the base image for deeper folds/shadows
    # A simple way to boost contrast in the shadows while keeping highlights:
    # contrast_base = base_float^1.5 (gamma curve)
    contrast_base = np.power(base_float, 1.2)
    
    # Blending with contrast base for deeper folds
    blended_region = contrast_base * displaced_color_float
    
    final_img_float = base_float * (1 - displaced_mask_3c) + blended_region * displaced_mask_3c
    final_img = (final_img_float * 255).clip(0, 255).astype(np.uint8)

    cv2.imwrite(output_path, final_img)
    return output_path
