from django.contrib import admin
from .models import Question,Product,Order,FAQ

# Register your models here.

admin.site.register(Question)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(FAQ)

