from django.urls import path
from .views import ProductListView, MockupRequestView, MockupStatusView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('mockup/request/', MockupRequestView.as_view(), name='mockup-request'),
    path('mockup/status/<str:task_id>/', MockupStatusView.as_view(), name='mockup-status'),
]
