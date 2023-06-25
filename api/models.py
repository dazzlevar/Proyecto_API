from django.db import models

# Create your models here.


class Company(models.Model):
    name = models.CharField(max_length=50)
    website = models.URLField(max_length=100)
    foundation = models.PositiveIntegerField()

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    categoria_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    serie_producto = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/')
    fecha = models.DateField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
class Pedido(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pedido = models.CharField(max_length=50)
    fecha_pedido = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Pedido de {self.producto.nombre} - Estado: {self.estado_pedido}"


