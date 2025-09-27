from django.contrib import admin
from .models import User, ProducerProfile, BuyerProfile

admin.site.register(User)
admin.site.register(ProducerProfile)
admin.site.register(BuyerProfile)
