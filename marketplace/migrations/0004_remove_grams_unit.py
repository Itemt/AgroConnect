from django.db import migrations


def migrate_g_to_kg(apps, schema_editor):
    Publication = apps.get_model('marketplace', 'Publication')
    for pub in Publication.objects.filter(unidad_medida='g'):
        # Convertir la cantidad disponible y mínima de g a kg
        try:
            pub.cantidad_disponible = float(pub.cantidad_disponible) * 0.001
        except Exception:
            pass
        try:
            pub.cantidad_minima = float(pub.cantidad_minima) * 0.001
        except Exception:
            pass
        # Convertir precio: precio por g -> precio por kg (1 kg = 1000 g)
        try:
            pub.precio_por_unidad = float(pub.precio_por_unidad) * 1000
        except Exception:
            pass
        pub.unidad_medida = 'kg'
        pub.save()


class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', '0003_add_unit_conversion'),
    ]

    operations = [
        migrations.RunPython(migrate_g_to_kg, migrations.RunPython.noop),
    ]


