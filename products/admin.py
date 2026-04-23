from django.contrib import admin
from .models import Product, ProductView, PrintArea

class PrintAreaInline(admin.StackedInline):
    model = PrintArea

class ProductViewInline(admin.StackedInline):
    model = ProductView
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ProductViewInline]

@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name')
    inlines = [PrintAreaInline]

@admin.register(PrintArea)
class PrintAreaAdmin(admin.ModelAdmin):
    list_display = ('product_view',)
