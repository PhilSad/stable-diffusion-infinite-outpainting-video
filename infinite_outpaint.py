import click
from typing import List
from outpaint import generate_outpainted_images
from super_resolution import generate_base_images_ia
import os


def generate_base_images(prompts:List[str], n_steps:int, downscale_factor:int, save_folder:str):
    images = generate_outpainted_images(prompts, n_steps)

    for i, base_image in enumerate(generate_base_images_ia(images)):
        base_image.save(f'{save_folder}/{i}.jpeg')
        



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