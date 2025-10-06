# Generated manually to add area_ocupada field to Crop model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_crop_finca'),
    ]

    operations = [
        migrations.AddField(
            model_name='crop',
            name='area_ocupada',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Área que ocupa este cultivo en la finca',
                max_digits=10,
                verbose_name='Área Ocupada (hectáreas)'
            ),
        ),
    ]
