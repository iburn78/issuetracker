# This code is incomplete! 
# After getting the list, you have to manually delete files with sudo rm files
# -------------
# Image Clean-up code
# python manage.py shell
# exec(open("board/temp.py").read())

from board.models import Post
import os

def find_and_remove(item, lst, p):
    if item in lst:
        index = lst.index(item)  # Get the index of the item
        lst.pop(index)  # Remove the item
        return index
    else:
        print(f'ERROR {item} not exist')
        print(p.title)
        print(p.id)


cur_loc = r'media/uploaded/'
# media_path = ['post_imgs', 'ppost_imgs'] # for images
media_path = ['post_imgsr', 'ppost_imgsr'] # for thumbnails

image_files = [] # target to delete (not matched with posts)
image_path = []

# first get all image files and paths
for i in media_path:
    target_path = os.path.join(cur_loc, i)
    for root, dirs, files in os.walk(target_path):
        for file in files:
            image_files.append(file)
            image_path.append(root)


# pop out matched ones
for p in Post.objects.all():
    for i in range(1, 11):  
        # image_attr = f"image{i}"  # images
        image_attr = f"image{i}s"  # thumbnails
        image = getattr(p, image_attr, None)  
        if image:  
            image_name = os.path.basename(image.name)  
            index = find_and_remove(image_name, image_files, p)  
            image_path.pop(index)


print(image_files)
print(image_path)

res = []
for i in range(len(image_files)):
    fp = os.path.join(image_path[i], image_files[i])  
    if os.path.exists(fp):  
        res.append(image_files[i])
        print(fp)
    else:
        print('ERROR')


target_to_delete = ''
for item in res: 
    target_to_delete += item+' '


# use sudo to manually delete files....
print(target_to_delete)
