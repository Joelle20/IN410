import gradio as gr

from encrypt import encrypt_file
from decrypt import decrypt_file


def show_input(file):
    if file is None:
        return ""
    with open(file.name, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()



def encrypt_ui(file):
    input_path = file.name
    output_path = "Cipher.md"

    encrypt_file(input_path, output_path)

    with open(output_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read(), output_path   # preview + file



def decrypt_ui(file):
    input_path = file.name
    output_path = "Recovered.md"

    decrypt_file(input_path, output_path)

    with open(output_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read(), output_path


with gr.Blocks() as app:

    gr.Markdown("# 🔐 XEX Encryption / Decryption Tool")

    file_input = gr.File(label="📂 Choose File")

    input_preview = gr.Textbox(label="👀 Input Preview", lines=10)

    file_input.change(
        fn=show_input,
        inputs=file_input,
        outputs=input_preview
    )

    with gr.Row():
        enc_btn = gr.Button("Encrypt 🔐")
        dec_btn = gr.Button("Decrypt 🔓")

    output_preview = gr.Textbox(label="📤 Output Preview", lines=10)
    output_file = gr.File(label="📥 Download Result")


    enc_btn.click(
        fn=encrypt_ui,
        inputs=file_input,
        outputs=[output_preview, output_file]
    )

    dec_btn.click(
        fn=decrypt_ui,
        inputs=file_input,
        outputs=[output_preview, output_file]
    )

app.launch()