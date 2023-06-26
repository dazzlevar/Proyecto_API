
import json
from datetime import date
import uuid
from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import Categoria, Producto, Pedido
from django.db.models import Subquery, OuterRef
from datetime import date
from django.http import JsonResponse
from django.conf import settings

class CategoriaView(View):
    def get(self, request, id=0):
        if id > 0:
            try:
                categoria = Categoria.objects.get(id=id)
                datos = {'message': 'Success', 'categoria': {'id': categoria.id, 'nombre': categoria.nombre, 'categoria_padre': categoria.categoria_padre_id}}
            except Categoria.DoesNotExist:
                datos = {'message': 'Categoria not found...'}
        else:
            categorias = list(Categoria.objects.values())
            datos = {'message': 'Success', 'categorias': categorias}
        return JsonResponse(datos)
    
    def post(self, request):
        jd = json.loads(request.body)
        nombre = jd.get('nombre')
        categoria_padre_id = jd.get('categoria_padre_id')
        categoria = Categoria.objects.create(nombre=nombre, categoria_padre_id=categoria_padre_id)
        datos = {'message': 'Success', 'categoria': {'id': categoria.id, 'nombre': categoria.nombre, 'categoria_padre': categoria.categoria_padre_id}}
        return JsonResponse(datos)
    
    def put(self, request, id):
        jd = json.loads(request.body)
        try:
            categoria = Categoria.objects.get(id=id)
            categoria.nombre = jd.get('nombre', categoria.nombre) 
            categoria.categoria_padre_id = jd.get('categoria_padre_id', categoria.categoria_padre_id)   
            categoria.save()
            datos = {'message': 'Success'}
        except Categoria.DoesNotExist:
            datos = {'message': 'Categoria not found...'}
        return JsonResponse(datos)
    
    def delete(self, request, id):
        try:
            categoria = Categoria.objects.get(id=id)
            categoria.delete()
            datos = {'message': 'Success'}
        except Categoria.DoesNotExist:
            datos = {'message': 'Categoria not found...'}
        return JsonResponse(datos)





class ProductoView(View):
    def get_image_url(self, image):
        if image:
            return settings.MEDIA_URL + image.name
        return None

    def get(self, request, id=None):
        if id is not None:
            try:
                producto = Producto.objects.get(id=id)
                datos = {
                    'message': 'Success',
                    'producto': {
                        'id': producto.id,
                        'nombre': producto.nombre,
                        'precio': str(producto.precio),
                        'stock': producto.stock,
                        'categoria': {'id': producto.categoria.id, 'nombre': producto.categoria.nombre},
                        'imagen': self.get_image_url(producto.image)
                    }
                }
            except Producto.DoesNotExist:
                datos = {'message': 'Producto not found...'}
        else:
            productos = Producto.objects.values('id', 'nombre', 'precio', 'stock', 'categoria__id', 'categoria__nombre', 'image')
            datos = {'message': 'Success', 'productos': list(productos)}
        return JsonResponse(datos)

    def post(self, request):
        jd = json.loads(request.body)
        categoria_id = jd['categoria_id']
        try:
            categoria = Categoria.objects.get(id=categoria_id)
            producto = Producto.objects.create(
                serie_producto=jd['serie_producto'],
                marca=jd['marca'],
                nombre=jd['nombre'],
                codigo=jd['codigo'],
                precio=jd['precio'],
                stock=jd['stock'],
                image=jd['image'],
                fecha=date.today(),
                categoria=categoria
            )
            datos = {
                'message': 'Success',
                'producto': {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'precio': str(producto.precio),
                    'stock': producto.stock,
                    'categoria': {
                        'id': producto.categoria.id,
                        'nombre': producto.categoria.nombre
                    }
                }
            }
        except Categoria.DoesNotExist:
            datos = {'message': 'Categoria not found...'}
        return JsonResponse(datos)
    def put(self, request, id):
        jd = json.loads(request.body)
        try:
            producto = Producto.objects.get(id=id)
            categoria_id = jd['categoria_id']
            try:
                categoria = Categoria.objects.get(id=categoria_id)
                producto.serie_producto = jd['serie_producto']
                producto.marca = jd['marca']
                producto.nombre = jd['nombre']
                producto.codigo = jd['codigo']
                producto.precio = jd['precio']
                producto.stock = jd['stock']
                producto.fecha = date.today()
                producto.categoria = categoria
                producto.save()
                datos = {'message': 'Success'}
            except Categoria.DoesNotExist:
                datos = {'message': 'Categoria not found...'}
        except Producto.DoesNotExist:
            datos = {'message': 'Producto not found...'}
        return JsonResponse(datos)
    def delete(self, request, id):
        try:
            producto = Producto.objects.get(id=id)
            producto.delete()
            datos = {'message': 'Success'}
        except Producto.DoesNotExist:
            datos = {'message': 'Producto not found...'}
        return JsonResponse(datos)

class PedidoView(View):
    @method_decorator(csrf_exempt)
    def get(self, request, id=None):
        if id:
            try:
                pedido = Pedido.objects.prefetch_related('productos__categoria').get(id=id)
                productos = pedido.productos.all()
                datos = {
                    'message': 'Success',
                    'pedido': self.serialize_pedido(pedido, productos)
                }
            except Pedido.DoesNotExist:
                datos = {'message': 'Pedido not found...'}
        else:
            pedidos = Pedido.objects.prefetch_related('productos__categoria').all()
            datos = {
                'message': 'Success',
                'pedidos': [
                    self.serialize_pedido(pedido, pedido.productos.all())
                    for pedido in pedidos
                ]
            }
        return JsonResponse(datos)

    def serialize_pedido(self, pedido, productos):
        return {
            'id': pedido.id,
            'fecha_pedido': pedido.fecha_pedido.strftime('%Y-%m-%d'),
            'fecha_entrega': pedido.fecha_entrega.strftime('%Y-%m-%d') if pedido.fecha_entrega else None,
            'cantidad': pedido.cantidad,
            'precio_total': str(pedido.precio_total),
            'estado_pedido': pedido.estado_pedido,
            'productos': [{
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'stock': producto.stock,
                'categoria': {
                    'id': producto.categoria.id,
                    'nombre': producto.categoria.nombre
                }
            } for producto in productos]
        }




    def post(self, request):
        jd = json.loads(request.body)
        producto_ids = jd['producto_ids']
        cantidad = jd['cantidad']
        fecha_pedido = jd['fecha_pedido']  
        fecha_entrega = jd['fecha_entrega']  
        estado_pedido = jd['estado_pedido']  

        try:
            productos = Producto.objects.filter(id__in=producto_ids)
            if all(producto.stock > 0 for producto in productos):
                precio_total = sum(producto.precio for producto in productos)
                pedido = Pedido.objects.create(
                    fecha_pedido=fecha_pedido,
                    cantidad=cantidad,
                    precio_total=precio_total,
                    estado_pedido=estado_pedido,
                    fecha_entrega=fecha_entrega
                )
                pedido.productos.set(productos)
                for producto in productos:
                    producto.stock -= 1
                    producto.save()
                datos = {
                    'message': 'Success',
                    'pedido': {
                        'id': pedido.id,
                        'fecha_pedido': pedido.fecha_pedido.strftime('%Y-%m-%d'),
                        'fecha_entrega': pedido.fecha_entrega,
                        'cantidad': pedido.cantidad,
                        'precio_total': str(pedido.precio_total),
                        'estado_pedido': pedido.estado_pedido,
                        'productos': [{
                            'id': producto.id,
                            'nombre': producto.nombre,
                            'precio': str(producto.precio),
                            'stock': producto.stock,
                            'categoria': {
                                'id': producto.categoria.id,
                                'nombre': producto.categoria.nombre
                            }
                        } for producto in productos]
                    }
                }
            else:
                datos = {'message': 'One or more products are out of stock...'}
        except Producto.DoesNotExist:
            datos = {'message': 'Producto not found...'}
        return JsonResponse(datos)


    @method_decorator(csrf_exempt)
    def put(self, request, id):
        jd = json.loads(request.body)
        try:
            pedido = Pedido.objects.get(id=id)
            if 'producto_ids' in jd:
                producto_ids = jd['producto_ids']
                try:
                    productos = Producto.objects.filter(id__in=producto_ids)
                    if all(producto.stock > 0 for producto in productos):
                        pedido.productos.clear()
                        pedido.productos.set(productos)
                        for producto in productos:
                            producto.stock -= 1
                            producto.save()
                    else:
                        return JsonResponse({'message': 'One or more products are out of stock...'})
                except Producto.DoesNotExist:
                    return JsonResponse({'message': 'Producto not found...'})

            if 'cantidad' in jd:
                pedido.cantidad = jd['cantidad']
            if 'estado_pedido' in jd:
                pedido.estado_pedido = jd['estado_pedido']
            if 'fecha_entrega' in jd:
                pedido.fecha_entrega = jd['fecha_entrega']
            pedido.save()
            datos = {'message': 'Success'}
        except Pedido.DoesNotExist:
            datos = {'message': 'Pedido not found...'}
        return JsonResponse(datos)


    @method_decorator(csrf_exempt)
    def delete(self, request, id):
        try:
            pedido = Pedido.objects.prefetch_related('productos').get(id=id)
            productos = pedido.productos.all()
            for producto in productos:
                producto.stock += 1
                producto.save()
            pedido.delete()
            datos = {'message': 'Success'}
        except Pedido.DoesNotExist:
            datos = {'message': 'Pedido not found...'}
        return JsonResponse(datos)



class ProductoDiferentesView(View):
    @method_decorator(csrf_exempt)
    def get(self, request, categoria_id):
        subquery = Producto.objects.filter(categoria_id=categoria_id).values('nombre').distinct()
        productos = Producto.objects.filter(nombre__in=Subquery(subquery))

        if productos.exists():
            serialized_productos = [{'id': producto.id, 'nombre': producto.nombre} for producto in productos]

            datos = {'message': 'Success', 'productos': serialized_productos}
        else:
            datos = {'message': 'No products found for the specified category.'}

        return JsonResponse(datos)

