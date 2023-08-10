import gradio as gr
import PIL
from diffusers import StableDiffusionInpaintPipeline
from outpaint import downscale_and_perlin
import random
from super_resolution import generate_base_images_ia
import os
import torch

pipe = StableDiffusionInpaintPipeline.from_pretrained(
        "runwayml/stable-diffusion-inpainting", safety_checker=None).to('cuda')

def generate_outpaint(prompt,
                      num_images_per_prompt, 
                      num_inference_steps,
                      init_image):
    global out_images

    diff_init_img, diff_mask_img = downscale_and_perlin(init_image, 4)
    out_images = pipe(prompt=prompt, 
                      image=diff_init_img, 
                      mask_image=diff_mask_img, 
                      num_images_per_prompt=int(num_images_per_prompt),
                      num_inference_steps=int(num_inference_steps)).images
    
    return out_images, gr.update(interactive=True)

def accept_image(output_images):
    accepted_images.append(out_images[gallery_selected_idx])
    return accepted_images, out_images[gallery_selected_idx], gr.update(interactive=False) 

def on_image_select(evt:gr.SelectData):
    global gallery_selected_idx
    gallery_selected_idx = evt.index

def on_image_upload(input_image):
    accepted_images.append(input_image)
    return accepted_images

def generate_triplets(path):

    if not os.path.exists(path):
        os.makedirs(path)

    for f in os.listdir(path):
        os.remove(os.path.join(path, f))
    
    for i, base_image in enumerate(generate_base_images_ia(accepted_images)):
        base_image.save(f'{path}/{i}.jpeg')
    
    return gr.update(visible=True)
        
with gr.Blocks() as demo:
    accepted_images = []
    gallery_selected_idx = None

    out_images = None

    with gr.Row():
        num_inference_steps   = gr.Number(5, label="num_inference_steps")
        num_images_per_prompt = gr.Number(2, label="num_images_per_prompt")

    with gr.Row():
        prompt = gr.inputs.Textbox(lines=2, label="Prompt")
        generate_btn = gr.Button("Generate", interactive=False, variant="primary")

    with gr.Row():
        init_image = gr.Image(type="pil", label="Initial Image")

        with gr.Column():
            output_gallery = gr.Gallery(label="Output Images")
            output_gallery.select(on_image_select)

            accept_btn = gr.Button("Accept", interactive=False)
    
    with gr.Row():
        gallery = gr.Gallery(label="Accepted images")

    with gr.Row():
        save_path = gr.Textbox("/content/drive/MyDrive/stable-diffusion-infinite-outpaint/base_images", lines=1, label="save_path")
        generate_triplets_btn = gr.Button("Generate HQ Triplets (DELETE EVERYTHING IN SAVE FOLDER)", variant="primary")
    with gr.Row():
        done_triplet = gr.HTML('<b>Done generating triplet!</b> <br /> Now got to <a href="https://colab.research.google.com/github/PhilSad/stable-diffusion-infinite-outpainting-video/blob/main/notebooks/colab_infinite_outpaint_generate_video.ipynb"> this Colab to generate the video</a>', visible=False)

    init_image.upload(on_image_upload, init_image, gallery)

    generate_btn.click(generate_outpaint, inputs = [prompt, num_images_per_prompt,num_inference_steps, init_image] ,outputs=[output_gallery, accept_btn])
    accept_btn.click(accept_image, inputs=output_gallery, outputs=[gallery, init_image, accept_btn])
    generate_triplets_btn.click(generate_triplets, inputs=save_path, outputs=done_triplet)
    prompt.change(fn=lambda prompt: gr.update(interactive = len(prompt) > 0 ), inputs=prompt, outputs=generate_btn)
    # output_image.change(fn=lambda image: gr.update(interactive = image is not None ), inputs=output_image, outputs=accept_btn)

demo.launch(debug=True, share=True)