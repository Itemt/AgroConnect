from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cart.models import Cart

class Command(BaseCommand):
    help = 'Create carts for users that do not have one'

    def handle(self, *args, **options):
        User = get_user_model()
        users_without_cart = User.objects.filter(cart__isnull=True)
        for user in users_without_cart:
            Cart.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Successfully created cart for user "{user.username}"'))

        self.stdout.write(self.style.SUCCESS('Finished creating carts for users.'))
