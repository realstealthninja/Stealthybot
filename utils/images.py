import PIL
from PIL import Image
import numpy as np

def stichimgs(imglist:list,name):
    images = [PIL.Image.open(i) for i in imglist]
    min_shape = sorted([(np.sum(i.size), i.size) for i in images])[0][1]
    imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in images ) )
    
    imgs_comb = PIL.Image.fromarray( imgs_comb)
    imgs_comb.save(f'assets/stichedimages/{name}.png')
    return f'assets/stichedimages/{name}.png'

