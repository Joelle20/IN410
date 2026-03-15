from xex_mode import xex_encrypt
from helper_fc import binary_to_text, load_keys

def encrypt_file(input_file, output_file):
    key1, key2, tweak, alpha, pad = load_keys()
    with open(input_file, 'r') as f:
        content = f.read()
    content = content.replace(" ", "")
    if len(content) % 2 != 0:
        content += pad

    encrypted_blocks = []

    j = 0
    for i in range(0, len(content), 2):
        block = content[i:i+2]
        cipher = xex_encrypt(block, key1, key2, tweak, alpha, j)
        encrypted_blocks.append(binary_to_text(cipher))
        j += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("".join(encrypted_blocks))


encrypt_file("Text.txt", "Cipher.txt")