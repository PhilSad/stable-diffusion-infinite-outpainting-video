import click
import PIL
from PIL import Image
import cv2
import numpy as np
import random
from perlin_noise import PerlinNoise
from sd_outpaint.downscale_and_noise import get_init_mask_image
import requests
import torch
from io import BytesIO
from PIL import Image
from diffusers import StableDiffusionInpaintPipeline
import numpy as np
import time
from diffusers import StableDiffusionPipeline







def generate_outpainted_images(prompts, n_images):
    prompt = prompts[0] #todo take multiple prompts sequentialy
    print('generating first image')
    # Generate first image
    pipe_txt2img = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1")
    pipe_txt2img.to('cuda')    
    cur_image = pipe_txt2img(prompt).images[0]
    del pipe_txt2img
    
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        "runwayml/stable-diffusion-inpainting").to('cuda')
    pipe.enable_attention_slicing() 
    
    print('generating outpainted images')
    for i in range(n_images):
        print('STEP: ', i)
        init_image, mask_image = get_init_mask_image(cur_image)
        cur_image = pipe(prompt=prompt, image=Image.fromarray(init_image), mask_image=Image.fromarray(mask_image)).images[0]
        #todo rendre trensparent les pixels du masque de l'image précédente
        cur_image.save(f'./save/{str(i)}.png')
