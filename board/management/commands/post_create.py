import os
from pathlib import Path
from django.core.management.base import BaseCommand
from users.models import User
from board.models import Card, Post
from django.core.files import File
from board.tools import *
from django.db import transaction

# the following code creates only basic posts:
# should not try to assign likes, dislikes, tags as they require m2m save. 
# also the author is fixed with id = 1

author_ID = 1
class Command(BaseCommand):
    help = "Creating a Post with images for the author Andy"

    def add_arguments(self, parser):
        parser.add_argument('card_id', type=int, help="ID of the Card to associate the post with")
        parser.add_argument('images', nargs='+', type=str, help="Paths to local images (up to 10)")

    def handle(self, *args, **options):
        card_id = options['card_id']
        image_paths = options['images']

        # Step 1: Ensure card exists
        try:
            card = Card.objects.get(id=card_id)
        except Card.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Card with ID {card_id} does not exist."))
            return

        # Step 3: Prepare the Post instance
        user = User.objects.get(id=author_ID)
        post = Post(
            card=card,
            author=user,
            content="CONTENT HAS TO BE GIVEN",
            num_images=min(len(image_paths), 10),
            is_html=False,
        )
            # Step 4: Attach Images
        image_fields = ['image1', 'image2', 'image3', 'image4', 'image5', 'image6', 'image7', 'image8', 'image9', 'image10']
        open_files = []
        for i, img_path in enumerate(image_paths[:10]):  # Max 10 images
            if not os.path.exists(img_path):
                self.stdout.write(self.style.WARNING(f"Image path does not exist: {img_path}"))
                raise Exception("CHECK IMAGE PATH")
            img_file = open(img_path, 'rb')
            open_files.append(img_file)
            _, ext = os.path.splitext(img_path)
            filename = f"image{i+1}{ext}"
            setattr(post, image_fields[i], File(img_file, name=filename))

        with transaction.atomic():
            # Step 5: Save the Post
            post.save()

            for file_obj in open_files:
                file_obj.close()

            # Step 6: Resize Images
            post_image_resize(post)  # Resize and process images (e.g., create thumbnails)

            self.stdout.write(self.style.SUCCESS(f"Post created successfully with ID {post.id}!"))