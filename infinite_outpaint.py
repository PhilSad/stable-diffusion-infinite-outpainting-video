import click
from typing import List
from outpaint import generate_outpainted_images
from super_resolution import generate_base_images_ia
import os


def generate_base_images(prompts:List[str], n_steps:int, downscale_factor:int, hq_save_folder:str, sd_save_folder:str):
    images = generate_outpainted_images(prompts, n_steps, sd_save_folder)

    for i, base_image in enumerate(generate_base_images_ia(images)):
        base_image.save(f'{hq_save_folder}/{i}.jpeg')
        



@click.command()
@click.option('--prompts_path', help='Path of the file containing the prompt inputs (one prompt per line)')
@click.option('--n_steps', default=5, help='How many downscale&outpainting steps')
@click.option('--downscale_factor',default=4, help='downscale by how much')
@click.option('--hq_save_folder', help='In wich folder to save the hd base pics for the video')
@click.option('--sd_save_folder', help='In wich folder to save the intermediary 512x512 SD pics.')
def cmd_generate_base_images(prompts_path:str, n_steps:int, downscale_factor:int, save_folder:str):
    if not os.path.exists(hq_save_folder):
        os.makedirs(hq_save_folder)
    if not os.path.exists(sd_save_folder):
        os.makedirs(sd_save_folder)

    with open(prompts_path, 'r') as f:
        prompts = f.read().splitlines()
        print(prompts)
    
    generate_base_images(prompts, n_steps, downscale_factor, hq_save_folder, sd_save_folder)



if __name__ == '__main__':
    cmd_generate_base_images()