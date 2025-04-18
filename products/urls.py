from django.urls import path
from .views import ProductListCreateView, ProductRetrieveUpdateDeleteView

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<str:id>/', ProductRetrieveUpdateDeleteView.as_view(), name='product-detail'),
]