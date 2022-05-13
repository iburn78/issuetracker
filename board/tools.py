from PIL import Image, ImageOps
from django.conf import settings
import os
from io import BytesIO
from django.core.files.base import ContentFile
from datetime import datetime
POST_IMG_MAXSIZE = 2000


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

  wa = []
  ha = []
  hh = []
  wh = []
  for i in range(0, post.num_images): 
    with Image.open(images[i].file) as img:
      img = ImageOps.exif_transpose(img)
      w, h = img.size
      wa.append(w)
      ha.append(h)
      hh.append(h*h)
      wh.append(w*h)

  ar = float(sum(hh)/sum(wh))

  croparea = []
  for i in range(0, post.num_images): 
    w = wa[i]
    h = ha[i]
    if ar >= h/w:
      croparea.append(((w-h/ar)/2, 0, (w+h/ar)/2, h))
    else: 
      croparea.append((0, (h-w*ar)/2, w, (h+w*ar)/2))

  for i in range(0, post.num_images): 
    img_io = BytesIO()
    img = Image.open(images[i].file)
    img_exif = ImageOps.exif_transpose(img)
    res = img_exif.crop(croparea[i])
    res = image_resize(POST_IMG_MAXSIZE, res)
    res.save(img_io, format=img.format)
    th_images[i].save(os.path.basename(images[i].file.name), ContentFile(img_io.getvalue()))

def exception_log(text): 
  logfilepath = os.path.join(settings.BASE_DIR, 'etc') 
  with open(os.path.join(logfilepath, 'exception_log.txt'), 'a') as logfile: 
    now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    logfile.write(now + " " + text + "\n")


# from pathlib import Path
# import json
# import os

# BASE_DIR = Path(__file__).resolve().parent.parent
# i1 = Image.open(os.path.join(BASE_DIR,'media/temp/background.jpg'))
# i2 = Image.open(os.path.join(BASE_DIR,'media/temp/cap.JPG'))
# i3 = Image.open(os.path.join(BASE_DIR,'media/temp/xooos.JPG'))

# wa = []
# ha = []
# hh = []
# wh = []
# for i in [i1, i2, i3]:
#   w, h = i.size
#   print('before')
#   print(w,h)
#   img = ImageOps.exif_transpose(i)
#   w, h = img.size
#   print('after')
#   print(w,h)
#   wa.append(w)
#   ha.append(h)
#   hh.append(h*h)
#   wh.append(w*h)

# ar = float(sum(hh)/sum(wh))

# for i in [i1, i2, i3]:
#   w, h = img.size
#   if ar >= h/w:
#     croparea = ((w-h/ar)/2, 0, (w+h/ar)/2, h)
#   else: 
#     croparea = (0, (h-w*ar)/2, w, (h+w*ar)/2)
#   print(ar)
#   print(croparea)
