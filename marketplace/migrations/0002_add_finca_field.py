# Generated manually to add finca field to Publication model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
        ('core', '0002_farm'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='finca',
            field=models.ForeignKey(
                blank=True, 
                null=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                related_name='publicaciones', 
                to='core.farm', 
                verbose_name='Finca de Origen'
            ),
        ),
    ]
