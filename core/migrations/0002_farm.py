# Generated manually for Farm model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Farm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=255, verbose_name='Nombre de la Finca')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('departamento', models.CharField(max_length=100, verbose_name='Departamento')),
                ('ciudad', models.CharField(max_length=100, verbose_name='Ciudad/Municipio')),
                ('direccion', models.TextField(verbose_name='Dirección')),
                ('coordenadas_lat', models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True, verbose_name='Latitud')),
                ('coordenadas_lng', models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True, verbose_name='Longitud')),
                ('area_total', models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(0.01)], verbose_name='Área Total (hectáreas)')),
                ('area_cultivable', models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(0.01)], verbose_name='Área Cultivable (hectáreas)')),
                ('tipo_suelo', models.CharField(choices=[('arcilloso', 'Arcilloso'), ('arenoso', 'Arenoso'), ('limoso', 'Limoso'), ('franco', 'Franco'), ('orgánico', 'Orgánico'), ('mixto', 'Mixto')], max_length=20, verbose_name='Tipo de Suelo')),
                ('tipo_riego', models.CharField(choices=[('natural', 'Natural (Lluvia)'), ('goteo', 'Goteo'), ('aspersión', 'Aspersión'), ('inundación', 'Inundación'), ('mixto', 'Mixto')], max_length=20, verbose_name='Tipo de Riego')),
                ('certificacion_organica', models.BooleanField(default=False, verbose_name='Certificación Orgánica')),
                ('certificacion_bpa', models.BooleanField(default=False, verbose_name='Certificación BPA')),
                ('otras_certificaciones', models.TextField(blank=True, null=True, verbose_name='Otras Certificaciones')),
                ('activa', models.BooleanField(default=True, verbose_name='Finca Activa')),
                ('propietario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fincas', to=settings.AUTH_USER_MODEL, verbose_name='Propietario')),
            ],
            options={
                'verbose_name': 'Finca',
                'verbose_name_plural': 'Fincas',
                'ordering': ['-created_at'],
            },
        ),
    ]
