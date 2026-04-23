from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ProductView(models.Model):
    product = models.ForeignKey(Product, related_name='views', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="e.g., 'Front', 'Back', 'Side'")
    base_image = models.ImageField(upload_to='products/base_images/')

    def __str__(self):
        return f"{self.product.name} - {self.name}"

class PrintArea(models.Model):
    product_view = models.OneToOneField(ProductView, related_name='print_area', on_delete=models.CASCADE)
    
    # Perspective mapping coordinates (the 4 corners of the designated print area on the base image)
    top_left_x = models.IntegerField(help_text="X coordinate of the top-left corner")
    top_left_y = models.IntegerField(help_text="Y coordinate of the top-left corner")
    
    top_right_x = models.IntegerField()
    top_right_y = models.IntegerField()
    
    bottom_right_x = models.IntegerField()
    bottom_right_y = models.IntegerField()
    
    bottom_left_x = models.IntegerField()
    bottom_left_y = models.IntegerField()

    def __str__(self):
        return f"Print Area for {self.product_view}"
