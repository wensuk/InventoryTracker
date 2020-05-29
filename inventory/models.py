from django.db import models

# Create your models here.
class Brand(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Item(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Category(models.Model):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]
    name = models.CharField(max_length=64)
    status = models.CharField(max_length=64, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    category = models.ForeignKey(Category, max_length=64, null=False, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, null=False, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, null=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.category} {self.brand} {self.item}"

class Record(models.Model):
    name = models.CharField(max_length=128)
    rate = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, null=False, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} {self.rate} {self.quantity} {self.total}"

class Bill(models.Model):
    invoice = models.CharField(max_length=128, primary_key=True)
    date = models.CharField(max_length=128)
    company = models.CharField(max_length=128)
    reference = models.CharField(max_length=128, null=True)
    records = models.ManyToManyField(Record)

    def __str__(self):
        return f"{self.invoice} {self.date} {self.company}"

class Order(models.Model):
    invoice = models.CharField(max_length=128, primary_key=True)
    date = models.CharField(max_length=128)
    customer = models.CharField(max_length=128)
    reference = models.CharField(max_length=128, null=True)
    records = models.ManyToManyField(Record)

    def __str__(self):
        return f"{self.invoice} {self.date} {self.customer}"