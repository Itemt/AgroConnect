# Generated migration for migrating existing images to PublicationImage model

from django.db import migrations


def migrate_existing_images(apps, schema_editor):
    """Migra las imágenes existentes del campo 'imagen' al modelo PublicationImage"""
    Publication = apps.get_model('marketplace', 'Publication')
    PublicationImage = apps.get_model('marketplace', 'PublicationImage')
    
    for publication in Publication.objects.all():
        if publication.imagen:
            # Crear una PublicationImage con la imagen existente
            PublicationImage.objects.create(
                publication=publication,
                image=publication.imagen,
                is_primary=True,
                order=0
            )


def reverse_migrate_images(apps, schema_editor):
    """Reversa la migración copiando la primera imagen de vuelta al campo 'imagen'"""
    Publication = apps.get_model('marketplace', 'Publication')
    PublicationImage = apps.get_model('marketplace', 'PublicationImage')
    
    for publication in Publication.objects.all():
        first_image = PublicationImage.objects.filter(
            publication=publication
        ).order_by('order', 'id').first()
        
        if first_image:
            publication.imagen = first_image.image
            publication.save(update_fields=['imagen'])


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0005_alter_publication_unidad_medida_publicationimage'),
    ]

    operations = [
        migrations.RunPython(migrate_existing_images, reverse_migrate_images),
    ]
