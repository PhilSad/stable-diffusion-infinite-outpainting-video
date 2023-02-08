from RealESRGAN import RealESRGAN
from PIL import Image
import numpy as np
import torch

def get_pos_center(size_base, size_over):
  center = size_base // 2
  corner = center - size_over//2
  return (corner, corner)

def create_big_image_ia(im1,im2,im3):

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('device:', device)

    model_4x = RealESRGAN(device, scale=4)
    model_4x.load_weights(f'weights/RealESRGAN_x4.pth') 

    im1_newsize = im1.size[0] * 16
    im2_newsize = im2.size[0] * 4
    im3_newsize = im3.size[0] * 1

    print('first 4x')
    im1_big = model_4x.predict(im1)
    im1_big = im1_big.resize((im1_newsize,im1_newsize))
    print('second 4x')
    im2_big = model_4x.predict(im2)
    im3_big = im3.copy()



    pos_to_paste = get_pos_center(im1_newsize, im2_newsize)
    im1_big.paste(im2_big, pos_to_paste)

    pos_to_paste = get_pos_center(im1_newsize, im3_newsize)
    im1_big.paste(im3_big, pos_to_paste)

    return im1_big


def generate_base_images_ia(images):
    for im1,im2,im3 in zip(images, images[1:],images[2:]):
        yield create_big_image_ia(im3,im2,im1)
