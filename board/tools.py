from PIL import Image, ImageOps
from django.conf import settings
import os
from io import BytesIO
from django.core.files.base import ContentFile
from datetime import datetime
POST_IMG_MAXSIZE = 2000
IMG_ORIENTATION = 274 # exif code

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
      exception_log(text)

  if post.num_images == 0: 
    return None

  wa = []
  ha = []
  hh = []
  wh = []
  exif = []
  for i in range(0, post.num_images): 
    with Image.open(images[i].file) as img:
      try: 
        orientation = int(img._getexif()[IMG_ORIENTATION])
      except:
        orientation = 1
      if orientation >= 5:
        exif.append(True)
        h, w = img.size
      else: 
        exif.append(False)
        w, h = img.size
      wa.append(w)
      ha.append(h)
      hh.append(h*h)
      wh.append(w*h)

  try:
    ar = float(sum(hh)/sum(wh))
  except: 
    text = "Exception in ar calc. - def post_image_resize: "+ th_images[i].name  
    exception_log(text)
    ar = 1

  croparea = []
  for i in range(0, post.num_images): 
    w = wa[i]
    h = ha[i]
    if ar >= h/w:
      if exif[i]: 
        croparea.append((0, (w-h/ar)/2, h, (w+h/ar)/2)) # transpose
      else:
        croparea.append(((w-h/ar)/2, 0, (w+h/ar)/2, h))
    else: 
      if exif[i]: 
        croparea.append(((h-w*ar)/2, 0, (h+w*ar)/2, w)) # transpose 
      else:
        croparea.append((0, (h-w*ar)/2, w, (h+w*ar)/2))

  for i in range(0, post.num_images): 
    img_io = BytesIO()
    with Image.open(images[i].file) as img: 
      ft = img.format
      img = img.crop(croparea[i])
      img = image_resize(POST_IMG_MAXSIZE, img)
      res = ImageOps.exif_transpose(img)
      res.save(img_io, format=ft)
      th_images[i].save(os.path.basename(images[i].file.name), ContentFile(img_io.getvalue()))
      res.close()
  

def exception_log(text): 
  print("----->>>>>> ", text)
  logfilepath = os.path.join(settings.BASE_DIR, 'etc') 
  with open(os.path.join(logfilepath, 'exception_log.txt'), 'a') as logfile: 
    now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    logfile.write(now + " " + text + "\n")

