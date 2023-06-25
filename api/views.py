
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
                datos = {'message': 'Success', 'categoria': {'id': categoria.id, 'nombre': categoria.nombre}}
            except Categoria.DoesNotExist:
                datos = {'message': 'Categoria not found...'}
        else:
            categorias = list(Categoria.objects.values())
            datos = {'message': 'Success', 'categorias': categorias}
        return JsonResponse(datos)
    def post(self, request):
        jd = json.loads(request.body)
        categoria = Categoria.objects.create(nombre=jd['nombre'])
        datos = {'message': 'Success', 'categoria': {'id': categoria.id, 'nombre': categoria.nombre}}
        return JsonResponse(datos)
    def put(self, request, id):
        jd = json.loads(request.body)
        try:
            categoria = Categoria.objects.get(id=id)
            categoria.nombre = jd.get('nombre', categoria.nombre)  # Actualiza el nombre solo si está presente en jd
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
                pedido = Pedido.objects.select_related('producto').get(id=id)
                datos = {
                    'message': 'Success',
                    'pedido': {
                        'id': pedido.id,
                        'fecha': pedido.fecha.strftime('%Y-%m-%d'),
                        'producto': {
                            'id': pedido.producto.id,
                            'nombre': pedido.producto.nombre,
                            'precio': str(pedido.producto.precio),
                            'stock': pedido.producto.stock,
                            'categoria': {
                                'id': pedido.producto.categoria.id,
                                'nombre': pedido.producto.categoria.nombre
                            }
                        }
                    }
                }
            except Pedido.DoesNotExist:
                datos = {'message': 'Pedido not found...'}
        else:
            pedidos = Pedido.objects.select_related('producto').values('id', 'fecha', 'producto__id', 'producto__nombre', 'producto__precio', 'producto__stock', 'producto__categoria__id', 'producto__categoria__nombre')
            datos = {'message': 'Success', 'pedidos': list(pedidos)}
        return JsonResponse(datos)
    @method_decorator(csrf_exempt)
    def post(self, request):
        jd = json.loads(request.body)
        producto_id = jd['producto_id']
        try:
            producto = Producto.objects.get(id=producto_id)
            if producto.stock > 0:
                pedido = Pedido.objects.create(
                    fecha=date.today(),
                    producto=producto
                )
                producto.stock -= 1
                producto.save()
                datos = {
                    'message': 'Success',
                    'pedido': {
                        'id': pedido.id,
                        'fecha': pedido.fecha.strftime('%Y-%m-%d'),
                        'producto': {
                            'id': pedido.producto.id,
                            'nombre': pedido.producto.nombre,
                            'precio': str(pedido.producto.precio),
                            'stock': pedido.producto.stock,
                            'categoria': {
                                'id': pedido.producto.categoria.id,
                                'nombre': pedido.producto.categoria.nombre
                            }
                        }
                    }
                }
            else:
                datos = {'message': 'Product out of stock...'}
        except Producto.DoesNotExist:
            datos = {'message': 'Producto not found...'}
        return JsonResponse(datos)

    def put(self, request, id):
        jd = json.loads(request.body)
        try:
            pedido = Pedido.objects.get(id=id)
            if 'producto' in jd:
                try:
                    producto = Producto.objects.get(id=jd['producto'])
                    pedido.producto = producto
                except Producto.DoesNotExist:
                    return JsonResponse({'message': 'Producto not found...'})

            if 'precio' in jd:
                pedido.precio = jd['precio']
            if 'estado_pedido' in jd:
                pedido.estado_pedido = jd['estado_pedido']
            pedido.save()
            data = {'message': 'Success'}
        except Pedido.DoesNotExist:
            data = {'message': 'Pedido not found...'}
        return JsonResponse(data)

    @method_decorator(csrf_exempt)
    def delete(self, request, id):
        try:
            pedido = Pedido.objects.select_related('producto').get(id=id)
            producto = pedido.producto
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
        # Obtener productos diferentes en la misma categoría
        subquery = Producto.objects.filter(categoria_id=categoria_id).values('nombre').distinct()
        productos = Producto.objects.filter(nombre__in=Subquery(subquery))

        if productos.exists():
            # Serializar los productos si es necesario
            serialized_productos = [{'id': producto.id, 'nombre': producto.nombre} for producto in productos]

            # Devolver la respuesta JSON con los productos
            datos = {'message': 'Success', 'productos': serialized_productos}
        else:
            datos = {'message': 'No products found for the specified category.'}

        return JsonResponse(datos)


# class CompanyView(View):

#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)

#     def get(self, request, id=0):
#         if (id > 0):
#             companies = list(Company.objects.filter(id=id).values())
#             if len(companies) > 0:
#                 company = companies[0]
#                 datos = {'message': "Success", 'company': company}
#             else:
#                 datos = {'message': "Company not found..."}
#             return JsonResponse(datos)
#         else:
#             companies = list(Company.objects.values())
#             if len(companies) > 0:
#                 datos = {'message': "Success", 'companies': companies}
#             else:
#                 datos = {'message': "Companies not found..."}
#             return JsonResponse(datos)

#     def post(self, request):
#         jd = json.loads(request.body)
#         Company.objects.create(name=jd['name'], website=jd['website'], foundation=jd['foundation'])
#         datos = {'message': "Success"}
#         return JsonResponse(datos)

#     def put(self, request, id):
#         jd = json.loads(request.body)
#         companies = list(Company.objects.filter(id=id).values())
#         if len(companies) > 0:
#             company = Company.objects.get(id=id)
#             company.name = jd['name']
#             company.website = jd['website']
#             company.foundation = jd['foundation']
#             company.save()
#             datos = {'message': "Success"}
#         else:
#             datos = {'message': "Company not found..."}
#         return JsonResponse(datos)

#     def delete(self, request, id):
#         companies = list(Company.objects.filter(id=id).values())
#         if len(companies) > 0:
#             Company.objects.filter(id=id).delete()
#             datos = {'message': "Success"}
#         else:
#             datos = {'message': "Company not found..."}
#         return JsonResponse(datos)
