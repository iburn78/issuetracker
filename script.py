# use python manage.py shell < script.py
# or import script in shell (reload is not possible, variable scope issues might exist)
# or exec(open('script.py').read()) 

from board.models import Post, Card
from django.db.models.fields.files import ImageFieldFile, FileField

# Post.objects.all().delete()

img3 = ImageFieldFile(instance=Post, field=FileField(), name='uploaded_imgs/cap01.JPG')
# img2 = ImageFieldFile(instance=Post, field=FileField(), name='uploaded_imgs/xooos.JPG')
p3 = Post(author_id=4, card_id = 1, content ='p1', image1 = img3)
# p2 = Post(author_id=4, card_id = 1, content ='p2', image1 = img2)
p3.save()

# p1.image1.delete()
# p2.image1.delete() 


# **************
# there are errors asscoiated with delete()!!!!!!!!!!!!! with django-cleanup!!
# **************
