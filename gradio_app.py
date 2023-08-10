import gradio as gr

with gr.Blocks() as demo:
    accepted_images = []

    with gr.Row():
        prompt = gr.inputs.Textbox(lines=2, label="Prompt")
        generate_btn = gr.Button("Generate")

    with gr.Row():
        init_image = gr.Image(shape=(512, 512, 3), label="Initial Image")

        with gr.Column():
            output_image = gr.Image(label="Output Image")
            accept_btn = gr.Button("Accept")
    
    with gr.Row():
        gallery = gr.Gallery(accepted_images, label="Gallery")


demo.launch(debug=True)
