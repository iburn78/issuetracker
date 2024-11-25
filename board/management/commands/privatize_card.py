from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from board.models import Card 
from users.models import User

class Command(BaseCommand):
    help = 'Manage posts and cards in the IssueTracker database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--manager', 
            type=str, 
            help='Username of the public card manager'
        )
        parser.add_argument(
            '--privatize',
            type=str,
            help='Enter the card title to privatize: long enough to identify one card.'
        )

    def handle(self, *args, **kwargs):
        if kwargs['manager']:
            username = kwargs.get('manager')
            try:
                manager = User.objects.get(username=username)
                if not manager.is_public_card_manager:
                    self.stdout.write(self.style.WARNING(f"This is not a public card manager."))
                    return None
            except: 
                self.stdout.write(self.style.WARNING(f"No such manager"))
                return None
        else:
            self.stdout.write(self.style.WARNING(f"Manager username has to be given."))
            return None

        if kwargs['privatize']:
            card_keyword = kwargs.get('privatize')
            try: 
                card = Card.objects.get(title__icontains=card_keyword)  # Use `icontains` for case-insensitive search
            except ObjectDoesNotExist:
                self.stdout.write(self.style.ERROR(f"No card found with the keyword."))
                return None
            except MultipleObjectsReturned:
                self.stdout.write(self.style.ERROR(f"Multiple cards found with the keyword."))
                return None
            if card.owner == manager: 
                card.is_public = False
                card.is_official = False
                card.save()
                self.stdout.write(self.style.SUCCESS(f"Card is privatized to the manager {username} (as a non-official card)."))
            else:
                self.stdout.write(self.style.ERROR(f"Card owner is NOT the same as the manager {username}."))
                return None
            return 
