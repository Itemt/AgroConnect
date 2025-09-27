from django.db import models
from django.conf import settings
from core.models import BaseModel
from marketplace.models import Publication

# Create your models here.

class Conversation(BaseModel):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='conversations')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')

    def __str__(self):
        return f"Conversation about {self.publication.pk}"

class Message(BaseModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender} in conversation {self.conversation.pk}"


class Order(BaseModel):
    STATUS_CHOICES = (
        ('acordado', 'Acordado'),
        ('en tránsito', 'En tránsito'),
        ('entregado', 'Entregado'),
    )
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='orders')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_as_buyer')
    agreed_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f'Order {self.id} for {self.publication}'
