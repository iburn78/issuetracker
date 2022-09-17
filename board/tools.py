import cv2 as cv
import pathlib
from django.conf import settings
import os
from os.path import join as pj
from django.core.files.base import ContentFile
from datetime import datetime

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


def image_resize(maxsize, img):
    h, w, dim = img.shape
    if w <= h:
        if h <= maxsize:
            res = img
        else:
            wr = round(w/h*maxsize)
            hr = maxsize
            res = cv.resize(img, (wr, hr))
    else:
        if w <= maxsize:
            res = img
        else:
            wr = maxsize
            hr = round(h/w*maxsize)
            res = cv.resize(img, (wr, hr))
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
            img = cv.imread(def_img_location)
            filename = os.path.basename(def_img)
        else:
            img = cv.imread(form.instance.image.file.name)
            filename = os.path.basename(form.instance.image.name)
    else:
        name = form.instance.image.name
        try:
            if os.path.basename(os.path.dirname(name)) != CARD_DEFAULT_IMAGES:
                form.instance.image.delete()
        except:
            text = "Exception in delete cared image - card_image_resize: " + name
            exception_log(text)
        img = cv.imread(form.cleaned_data['image_input'].file.name)
        filename = os.path.basename(form.cleaned_data['image_input'].name)

    img = image_resize(CARD_IMAGE_MAXSIZE, img)
    ext = pathlib.Path(filename).suffix
    ret, buf = cv.imencode(ext, img)
    content = ContentFile(buf.tobytes())
    form.instance.image.save(filename, content)


def post_image_resize(post) -> None:
    images = [post.image1, post.image2, post.image3, post.image4, post.image5, post.image6, post.image7]
    th_images = [post.image1s, post.image2s, post.image3s, post.image4s, post.image5s, post.image6s, post.image7s]
    for i in range(0, 7):
        try:
            if th_images[i].name != "":
                th_images[i].delete()
        except:
            text = "Exception in delete images - def post_image_resize: " + th_images[i].name
            exception_log(text)

    if post.num_images == 0:
        return None

    wa = []
    ha = []
    hh = []
    wh = []
    cvimg = []
    for i in range(0, post.num_images):
        cvimg.append(cv.imread(images[i].file.name))
        h, w, dim = cvimg[i].shape
        wa.append(w)
        ha.append(h)
        hh.append(h*h)
        wh.append(w*h)
    try:
        ar = float(sum(hh)/sum(wh))
    except:
        text = "Exception in ar calc. - def post_image_resize: " + th_images[i].name
        ar = 1
        exception_log(text)

    croparea = []
    for i in range(0, post.num_images):
        w = wa[i]
        h = ha[i]
        if ar >= h/w:
            croparea.append((round((w-h/ar)/2), 0, round((w+h/ar)/2), h))
        else:
            croparea.append((0, round((h-w*ar)/2), w, round((h+w*ar)/2)))

    for i in range(0, post.num_images):
        cvimg[i] = cvimg[i][croparea[i][1]:croparea[i][3], croparea[i][0]:croparea[i][2]]
        cvimg[i] = image_resize(POST_IMG_MAXSIZE, cvimg[i])
        ext = pathlib.Path(images[i].file.name).suffix
        ret, buf = cv.imencode(ext, cvimg[i])
        content = ContentFile(buf.tobytes())
        th_images[i].save(os.path.basename(images[i].file.name), content)


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
