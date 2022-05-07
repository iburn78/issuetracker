from PIL import Image, ImageOps
from django.conf import settings
import os
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

def post_image_resize(imagefield) -> None:
  with Image.open(imagefield.file) as img:
    imgformat = img.format
    img = ImageOps.exif_transpose(img)
    img = image_resize(POST_IMG_MAXSIZE, img)
    img.save(os.path.join(settings.MEDIA_ROOT, imagefield.file.name), imgformat)