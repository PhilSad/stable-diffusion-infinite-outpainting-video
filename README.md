# stable-diffusion-infinite-outpainting-video

Generate an arbitrarly large zoom out / uncropping high quality (2K) video out of a list of prompt.

SD Exemple:

![demo_sd](https://user-images.githubusercontent.com/22277706/217584278-d870539c-c5ca-4464-b97f-26dccbc0ed84.gif)

HD 2K Exemple:

[youtube](https://youtu.be/1sxUNMEJ3Qg)

# Colab Usage

Thoses two steps need to be performed sequencialy:

* Step 1: [Generate 8k outpainting triplets (Need GPU)](https://colab.research.google.com/github/PhilSad/stable-diffusion-infinite-outpainting-video/blob/main/notebooks/colab_infinite_outpaint_generate_base_images.ipynb)
* Step 2: [Generate 2k video ( don't need GPU)](https://colab.research.google.com/github/PhilSad/stable-diffusion-infinite-outpainting-video/blob/main/notebooks/colab_infinite_outpaint_generate_video.ipynb)


## Note: google drive permission explaination
The first step (generation of the base image) need the GPU for stable diffusion & real-ersgan to generate HQ pictures with the GPU. Then each frame is generated on the CPU.
In order to save colab GPU time, each step is in its own collab file. Communication is made throught the mounted google drive folder.

# Install

Create a python env then:

```bash
git clone https://github.com/PhilSad/stable-diffusion-infinite-outpainting-video.git
cd stable-diffusion-infinite-outpainting-video
pip install -r requirements.txt
```

# Usage
BASE_IMAGE_DIR and BASE_VIDEO_DIR should be in their full path form.

```bash
# generate bases images for the video (Need GPU)
python infinite_outpaint.py --prompts_path input.txt --n_steps {N_STEPS} --downscale_factor 4 --save_folder {BASE_IMAGE_DIR}

# generate the video from the bases images (No GPU required)
python generate_video.py --base_images_fullpath {BASE_IMAGE_DIR} --save_videos_fullpath {BASE_VIDEO_DIR} --downscale_factor 4 
```

# known issues

The downscale_factor should be let at 4

# Citation

Please link to this repository if you use it in you projects


# How does it works?
## Outpaintings steps:
1. First prompt is generated using stablediffusion 2.1 txt2img 512x512 pix
2. Previous is scaled down by 4 and pasted at the center of a perlin image
3. Stable Diffusion inpainting model on image from step 2
4. Repeat step 2 & 3 n_steps times and save all 512x512 images

## HQ image generation
1. Create HQ (8K) frames out of consecutive triplets of outpainted images (im1,im2,im3).
2. Use Real-ERSGAN to upscale by 4 im3, then use PIL to expand by 4 another time (will be downscaled in the video)
3. Similarly, use Real-ERSGAN to upscale by 4 im2
4. Paste the 3 upscaled images on top of eachother at the center
5. Repeat 1,2,3,4 for each consecutive triplets of images

## Video generation
1. Take the first HQ image
2. Zoom x4 at the center and generate each frame by zooming out more and more to generate a frame list
3. Create a clip out of the frame list
4. Repeat 2 & 3 for each HQ image
5. Concat each clip to create the final video 
