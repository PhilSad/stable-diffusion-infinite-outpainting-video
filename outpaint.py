import cv2
import numpy as np
import random
from perlin_noise import PerlinNoise
from PIL import Image
from sklearn.preprocessing import minmax_scale
import PIL
import requests
import torch
from io import BytesIO
from PIL import Image
from itertools import cycle

from diffusers import StableDiffusionInpaintPipeline, StableDiffusionPipeline
noise11 = PerlinNoise(octaves=10)
noise12 = PerlinNoise(octaves=5)

noise21 = PerlinNoise(octaves=10)
noise22 = PerlinNoise(octaves=5)

noise31 = PerlinNoise(octaves=10)
noise32 = PerlinNoise(octaves=5)


def noise_mult_1(i,j, xpix=512,ypix=512):
  return noise11([i/xpix, j/ypix]) + 0.5 * noise12([i/xpix, j/ypix]) 

def noise_mult_2(i,j, xpix=512,ypix=512):
  return noise21([i/xpix, j/ypix]) + 0.5 * noise22([i/xpix, j/ypix]) 

def noise_mult_3(i,j, xpix=512,ypix=512):
  return noise31([i/xpix, j/ypix]) + 0.5 * noise32([i/xpix, j/ypix]) 

print('generating perlin image')
pic = [[[noise_mult_1(i,j), noise_mult_2(i,j), noise_mult_3(i,j) ] for j in range(512)] for i in range(512)]
scaled_noise = minmax_scale(np.array(pic).flatten(), (0,255)).reshape((512,512, 3))
perlin_img = Image.fromarray(scaled_noise.astype(np.uint8))

def get_pos_center(size_base, size_over):
  center = size_base // 2
  corner = center - size_over//2
  return (corner, corner)

def downscale_and_perlin(image: PIL.Image.Image, downscale_factor:int):
  dim = image.size[0]
  down_size = dim // downscale_factor

  init_img = perlin_img.copy()
  down_img = image.resize((down_size, down_size))
  pos_to_paste = get_pos_center(dim, down_size)
  init_img.paste(down_img, pos_to_paste)

  mask = Image.new( 'RGB',(512,512), '#FFFFFF')
  mask.paste(Image.new('RGB', (128,128), "#000000"), pos_to_paste)
  
  return init_img, mask


def generate_outpainted_images(prompts, n_images):
    torch.cuda.empty_cache()

    images = []

    prompt = prompts[0] #todo take multiple prompts sequentialy
    print('generating first image')
    # Generate first image
    pipe_txt2img = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1", revision='fp16', torch_dtype=torch.float16 , safety_checker=None)
    pipe_txt2img.to('cuda')   
    pipe_txt2img.enable_attention_slicing()
    cur_image = pipe_txt2img(prompt, height=512, width=512).images[0]
    images.append(cur_image)
    cur_image.save(f'./save2/0.png')
    del pipe_txt2img
    torch.cuda.empty_cache()

    
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        "runwayml/stable-diffusion-inpainting", safety_checker=None).to('cuda')
    pipe.enable_attention_slicing() 
    
    print('generating outpainted images')
    for i, prompt in zip(range(1, n_images), cycle(prompts[1:] + [prompts[0]])) :

        print('STEP: ', i, prompt)
        torch.cuda.empty_cache()

        init_image, mask_image  = downscale_and_perlin(cur_image, 4)
        cur_image = pipe(prompt=prompt, image=init_image, mask_image=mask_image).images[0]
        #todo rendre trensparent les pixels du masque de l'image précédente
        cur_image.save(f'./save2/{str(i)}.png')
        images.append(cur_image)
    return images

