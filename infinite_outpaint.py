import click
import PIL
from PIL import Image
import cv2
import numpy as np
import random
from perlin_noise import PerlinNoise
import requests
import torch
from io import BytesIO
from PIL import Image
from diffusers import StableDiffusionInpaintPipeline
import numpy as np
import time
from diffusers import StableDiffusionPipeline
from typing import List
from glob import glob
from outpaint import generate_outpainted_images
from super_resolution import generate_base_images_ia
import skvideo.io
import os

def create_zoom_video(img, output_filename, max_zoom=4, zoom_scale=1.01,  interpolation_method=cv2.INTER_CUBIC, size=(512,512) ):
    height, width = img.shape[:2]
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    # out = cv2.VideoWriter(output_filename, fourcc, 30.0, (512, 512))

    # Start from the original image
    frame = img.copy()
    zoom_factor = 1.0
    frames = []
    # Merci chatgpt
    while zoom_factor < max_zoom:
        print(zoom_factor)
        zoom_factor *= zoom_scale
        frame = cv2.resize(img, None, fx=zoom_factor, fy=zoom_factor)
        h, w = frame.shape[:2]
        x_offset = (w - width) // 2
        y_offset = (h - height) // 2
        frame = frame[y_offset:y_offset+height, x_offset:x_offset+width]
        frame = cv2.resize(frame, size)
        frames.append(frame)
    return frames

def generate_base_images(prompts:List[str], n_steps:int, downscale_factor:int, save_folder:str):
    images = generate_outpainted_images(prompts, n_steps)

    for i, base_image in enumerate(generate_base_images_ia(images)):
        base_image.save(f'{save_folder}/{i}.jpeg')
        


def generate_video(base_images_path:str, save_videos_path, downscale_factor:int):
    nb_images = len(list(glob.glob(f'{base_images_path}/*.jpeg')))
    
    for i in range(nb_images):
        with open(f'{base_images_path}/{i}.jpeg', 'rb') as f:
            cur_img = Image.open(f)
            f.load()
            
        print(i)
        frames=create_zoom_video(np.array(cur_img) , f'./videos/{str(i)}.avi', zoom_scale=1.02, size=(512*4,512*4), max_zoom=4)
        skvideo.io.vwrite(f"./{save_videos_path}/{str(i)}.mp4", np.array(list(reversed(frames))))
        del frames

    nb_clips = len(list(glob.glob(f'{base_images_path}/*.mp4')))
    with open('input.txt', 'w') as f:
        for i in range(nb_clips):
            f.write(f"./{save_videos_path}/{str(i)}.mp4")
    
    os.system('ffmpeg -f concat -safe 0 -i input.txt -c copy result.mp4 -y')
    
    
@click.command()
@click.option('--prompts_path', help='Path of the file containing the prompt inputs (one prompt per line)')
@click.option('--n_steps', default=5, help='How many downscale&outpainting steps')
@click.option('--downscale_factor',default=4, help='downscale by how much')
@click.option('--save_folder',  help='In wich folder saving the hd base pics for the video')
def cmd_generate_base_images(prompts_path:str, n_steps:int, downscale_factor:int, save_folder:str):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    with open(prompts_path, 'r') as f:
        prompts = f.read().splitlines()
        print(prompts)
    
    
    generate_base_images(prompts, n_steps, downscale_factor, save_folder)



if __name__ == '__main__':
    cmd_generate_base_images()