from PIL import Image, ImageOps
from django.conf import settings
import os
from os.path import join as pj
from io import BytesIO
from django.core.files.base import ContentFile
from datetime import datetime
import gc

USER_UPLOADS = 'uploaded' # to be included in .gitignore

CARD_IMAGE_MAXSIZE = 2000
CARD_DEFAULT_IMAGES = 'default_imgs'  
CARD_UPLOADED_IMGS = pj(USER_UPLOADS, 'card_imgs')   # url protected
CARD_PUBLIC_UPLOADED_IMGS = pj(USER_UPLOADS, 'pcard_imgs')

POST_IMG_MAXSIZE = 2000
POST_UPLOADED_IMGS = pj(USER_UPLOADS, 'post_imgs')   # url protected
POST_UPLOADED_IMGS_RESIZED = pj(USER_UPLOADS, 'post_imgsr')   # url protected
POST_PUBLIC_UPLOADED_IMGS = pj(USER_UPLOADS, 'ppost_imgs')   
POST_PUBLIC_UPLOADED_IMGS_RESIZED = pj(USER_UPLOADS, 'ppost_imgsr')

IMG_ORIENTATION = 274  # exif code
USER_DEFAULT_IMAGES = 'default_users'  
PROFILE_PICS = pj(USER_UPLOADS, 'profile_pics')

POST_MAX_COUNT_TO_DELETE_A_CARD = 10


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


def card_image_resize(form):
    if form.cleaned_data['image_input'] == None:
        def_img = form.cleaned_data['default_img']
        image_path = os.path.basename(os.path.dirname(form.instance.image.file.name))
        path_check_private = os.path.basename(CARD_UPLOADED_IMGS)
        path_check_public = os.path.basename(CARD_PUBLIC_UPLOADED_IMGS)
        if image_path == path_check_private or image_path == path_check_public:
            return None
        elif os.path.basename(os.path.dirname(def_img)) == CARD_DEFAULT_IMAGES: 
            def_img_location = os.path.join(settings.MEDIA_ROOT, def_img)
            img = Image.open(def_img_location)
            filename = os.path.basename(def_img)
        else:
            img = Image.open(form.instance.image.file)
            filename = os.path.basename(form.instance.image.name)
    else:
        name = form.instance.image.name
        try:
            if os.path.basename(os.path.dirname(name)) != CARD_DEFAULT_IMAGES:
                form.instance.image.delete()
        except:
            text = "Exception in delete cared image - card_image_resize: " + name
            exception_log(text)
        img = Image.open(form.cleaned_data['image_input'])
        filename = os.path.basename(form.cleaned_data['image_input'].name)

    img_io = BytesIO()
    ft = img.format
    img = image_resize(CARD_IMAGE_MAXSIZE, img)
    img = ImageOps.exif_transpose(img)
    img.save(img_io, format=ft)
    form.instance.image.save(filename, ContentFile(img_io.getvalue()))
    img.close()


def post_image_resize(post) -> None:
    images = [post.image1, post.image2, post.image3, post.image4, post.image5, post.image6, post.image7]
    th_images = [post.image1s, post.image2s, post.image3s, post.image4s, post.image5s, post.image6s, post.image7s]
    for i in range(0, 7):
        try:
            if th_images[i].name != "":
                th_images[i].delete()
        except:
            text = "Exception in delete images - def post_image_resize: " + \
                th_images[i].name
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
                orientation = int(img.getexif()[IMG_ORIENTATION])
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
        text = "Exception in ar calc. - def post_image_resize: " + \
            th_images[i].name
        exception_log(text)
        ar = 1

    croparea = []
    for i in range(0, post.num_images):
        w = wa[i]
        h = ha[i]
        if ar >= h/w:
            if exif[i]:
                croparea.append((0, round((w-h/ar)/2), h, round((w+h/ar)/2)))  # transpose
            else:
                croparea.append((round((w-h/ar)/2), 0, round((w+h/ar)/2), h))
        else:
            if exif[i]:
                croparea.append((round((h-w*ar)/2), 0, round((h+w*ar)/2), w))  # transpose
            else:
                croparea.append((0, round((h-w*ar)/2), w, round((h+w*ar)/2)))

    for i in range(0, post.num_images):
        img_io = BytesIO()
        with Image.open(images[i].file) as img:
            ft = img.format
            r1 = img.crop(croparea[i])
            r2 = image_resize(POST_IMG_MAXSIZE, r1)
            r3 = ImageOps.exif_transpose(r2)
            r3.save(img_io, format=ft)
            th_images[i].save(os.path.basename(images[i].file.name), ContentFile(img_io.getvalue()))
            r1.close()
            r2.close()
            r3.close()

def exception_log(text):
    print("----->>>>>> ", text)
    logfilepath = os.path.join(settings.BASE_DIR, 'etc')
    with open(os.path.join(logfilepath, 'exception_log.txt'), 'a') as logfile:
        now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        logfile.write(now + " " + text + "\n")


def exception_count(): 
    exp_file = os.path.join(settings.BASE_DIR, 'etc/exception_log.txt')
    with open(exp_file) as exp_log:
        return len(exp_log.readlines())
