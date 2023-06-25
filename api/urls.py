from django.urls import path
from .views import *

urlpatterns = [
    # Ruta para buscar productos diferentes en la misma categoría
    path('producto/categoria/<int:categoria_id>/diferentes/', ProductoDiferentesView.as_view(), name='producto-diferentes'),

    # Rutas para la clase Categoria
    path('categoria/', CategoriaView.as_view(), name='categoria-list'),
    path('categoria/<int:id>/', CategoriaView.as_view(), name='categoria-detail'),

    # Rutas para la clase Producto
    path('producto/', ProductoView.as_view(), name='producto-list'),
    path('producto/<int:id>/', ProductoView.as_view(), name='producto-detail'),

    # Rutas para la clase Pedido
    path('pedido/', PedidoView.as_view(), name='pedido-list'),
    path('pedido/<int:id>/', PedidoView.as_view(), name='pedido-detail'),
]
