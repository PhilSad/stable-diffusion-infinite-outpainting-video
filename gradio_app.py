import gradio as gr
import PIL

def generate_outpaint(prompt, init_image):
    
    # dummy code
    out_image = PIL.Image.open('./dummy.jpeg')
    return out_image, gr.update(interactive=True)

def accept_image(output_image):
    accepted_images.append(output_image)
    return accepted_images, gr.update(interactive=False)


with gr.Blocks() as demo:
    accepted_images = []

    with gr.Row():
        prompt = gr.inputs.Textbox(lines=2, label="Prompt")
        generate_btn = gr.Button("Generate", interactive=False, variant="primary")

    with gr.Row():
        init_image = gr.Image(shape=(512, 512, 3), label="Initial Image")

        with gr.Column():
            output_image = gr.Image(label="Output Image")
            accept_btn = gr.Button("Accept", interactive=False)
    
    with gr.Row():
        gallery = gr.Gallery(label="Accepted images")
    
    generate_btn.click(generate_outpaint, inputs = [prompt, init_image] ,outputs=[output_image, accept_btn])
    accept_btn.click(accept_image, inputs=output_image, outputs=[gallery, accept_btn])
    
    prompt.change(fn=lambda prompt: gr.update(interactive = len(prompt) > 0 ), inputs=prompt, outputs=generate_btn)
    output_image.change(fn=lambda image: gr.update(interactive = image is not None ), inputs=output_image, outputs=accept_btn)

demo.launch(debug=True)
