import os
import glob
from PIL import Image
import skvideo.io
import cv2
import click
import numpy as np

def create_zoom_video(img, max_zoom=4, zoom_scale=1.01,  interpolation_method=cv2.INTER_CUBIC, size=(512,512) ):
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

def generate_video(base_images_path:str, save_videos_path:str, downscale_factor:int):
    nb_images = len(list(glob.glob(f'./{base_images_path}/*.jpeg')))
    print(f'{nb_images} found, processing...')
    for i in range(nb_images):
        with open(f'{base_images_path}/{i}.jpeg', 'rb') as f:
            cur_img = Image.open(f)
            cur_img.load()
            
        print(i)
        frames=create_zoom_video(np.array(cur_img) , zoom_scale=1.02, size=(512*4,512*4), max_zoom=downscale_factor)
        skvideo.io.vwrite(f"./{save_videos_path}/{str(i)}.mp4", np.array(list(reversed(frames))))
        del frames

    nb_clips = len(list(glob.glob(f'{base_images_path}/*.mp4')))
    with open('input_ffmpeg.txt', 'w') as f:
        for i in range(nb_clips):
            f.write(f"./{save_videos_path}/{str(i)}.mp4")
    
    os.system('ffmpeg -f concat -safe 0 -i input_ffmpeg.txt -c copy result.mp4 -y')
    
    
@click.command()
@click.option('--base_images_path', help='Path of the folder containing the bases images')
@click.option('--save_videos_path', help='Where to save clips and final video')
@click.option('--downscale_factor',default=4, help='downscale by how much')
def cmd_generate_video(base_images_path:str, save_videos_path:str, downscale_factor:int):
    if not os.path.exists(save_videos_path):
        os.makedirs(save_videos_path)
    print('ran')
    generate_video(base_images_path, save_videos_path, downscale_factor)


if __name__ == '__main__':
    cmd_generate_video()