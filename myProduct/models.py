from django.db import models
from django.utils import timezone


class Category(models.Model):
    name  = models.CharField(max_length=100,null = False, blank = False)

    def __str__(self):
        return self.name
    


class Product(models.Model):
    name = models.CharField(max_length=200, null = False, blank = False)
    product_img = models.ImageField( null = False , upload_to='products')
    price  = models.IntegerField(null = False, blank = False)
    discount = models.IntegerField(null = False, blank = False , default = 0)
    description = models.CharField( max_length=500)
    instock = models.BooleanField( default = True)
    cate_id = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    @property
    def Discount_price(self):
        temp_data = 1.0 - (self.discount/100)
        discount_price = temp_data * self.price
        return round(discount_price)

    

class Customer(models.Model):
    name = models.CharField(max_length=200, null = False, blank = False)
    email = models.EmailField( max_length=254 )
    phone = models.CharField( max_length=100, null = False, blank = False)
    address = models.CharField( max_length=500)
    
    def __str__(self):
        return (f"{self.name}")
    

class Order(models.Model):
    price = models.IntegerField()
    qty = models.IntegerField(default= 1 )
    date = models.DateTimeField( null = False, blank = False , default = timezone.now)
    customer_id = models.ForeignKey(Customer,  on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product,  on_delete=models.CASCADE)
    
    def __str__(self):
        return (f"{self.product_id.name} order {self.qty} ")

    def priceQty(self):
        total = self.qty * self.price
        return total