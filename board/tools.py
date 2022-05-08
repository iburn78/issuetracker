from PIL import Image, ImageOps
from django.conf import settings
import os
from io import BytesIO
from django.core.files.base import ContentFile
POST_IMG_MAXSIZE = 700

def image_resize(maxsize, img: Image) -> Image:
  w, h = img.size
  if w <= h: 
    if h <= maxsize: 
      res = img
    else: 
      wr = round(w/h*maxsize)
      hr = maxsize
      res = img.resize((wr, hr))
  else: 
    if w <= maxsize:
      res = img
    else: 
      wr = maxsize
      hr = round(h/w*maxsize)
      res = img.resize((wr, hr))
  return res

# def post_image_resize(imagefield) -> None:
#   with Image.open(imagefield.file) as img:
#     img = ImageOps.exif_transpose(img)
#     img = image_resize(POST_IMG_MAXSIZE, img)
#     img.save(os.path.join(settings.MEDIA_ROOT, imagefield.file.name))


# from board.models import Post  # commented out to protect cirular import 
def post_image_resize(post) -> None:
  images = [post.image1, post.image2, post.image3, post.image4, post.image5, post.image6, post.image7]
  th_images = [post.image1s, post.image2s, post.image3s, post.image4s, post.image5s, post.image6s, post.image7s]
  for i in range(0, 7):
    try:
      if th_images[i].name != "":
        th_images[i].delete()
    except:
      text = "Exception in delete images - def post_image_resize: "+ th_images[i].name  
      print(text)
      exception_log(text)

  for i in range(0, post.num_images): 
    img_io = BytesIO()
    img = Image.open(images[i].file)
    img_exif = ImageOps.exif_transpose(img)
    # ****************************************************
    # ****************************************************
    # ****************************************************
    # ****************************************************
    res = img_exif.crop((0,0,700,700))
    # ****************************************************
    # ****************************************************
    # ****************************************************
    # ****************************************************
    res.save(img_io, format=img.format)
    th_images[i].save(os.path.basename(images[i].file.name), ContentFile(img_io.getvalue()))


def optimize_aspect_ratio(post) -> float:
  return 0.5


from datetime import datetime
def exception_log(text): 
  logfilepath = os.path.join(settings.BASE_DIR, 'etc') 
  with open(os.path.join(logfilepath, 'exception_log.txt'), 'a') as logfile: 
    now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    logfile.write(now + " " + text + "\n")
    