from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=255)
    answer_text = models.TextField()

    def __str__(self):
        return self.question_text

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name

class Order(models.Model):
    customer_name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, default="Pending")

    def __str__(self):
        return f'Order #{self.id} by {self.customer_name}'

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question