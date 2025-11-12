# Generated manually
import uuid
from django.db import migrations, models


def generate_unique_tokens(apps, schema_editor):
    """Genera tokens únicos para pedidos existentes"""
    Order = apps.get_model('sales', 'Order')
    for order in Order.objects.all():
        order.token_comprador = uuid.uuid4()
        order.token_vendedor = uuid.uuid4()
        order.save()


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_alter_order_estado'),
    ]

    operations = [
        # Paso 1: Agregar campos sin unique constraint
        migrations.AddField(
            model_name='order',
            name='token_comprador',
            field=models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Token QR Comprador', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='token_vendedor',
            field=models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Token QR Vendedor', null=True),
        ),
        # Paso 2: Generar tokens únicos para registros existentes
        migrations.RunPython(generate_unique_tokens, reverse_code=migrations.RunPython.noop),
        # Paso 3: Hacer los campos no nulos y únicos
        migrations.AlterField(
            model_name='order',
            name='token_comprador',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Token QR Comprador'),
        ),
        migrations.AlterField(
            model_name='order',
            name='token_vendedor',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Token QR Vendedor'),
        ),
    ]

