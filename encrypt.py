from xex_mode import xex_encrypt, compute_T0
from helper_fc import binary_to_text, load_keys


def encrypt_file(input_file, output_file):
    key1, key2, tweak, alpha, pad = load_keys()

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(" ", "")

    if len(content) % 2 != 0:
        content += pad

    T0 = compute_T0(key2, tweak)

    encrypted_blocks = []
    j = 0

    for i in range(0, len(content), 2):
        block = content[i:i+2]

        cipher_bits = xex_encrypt(block, key1, T0, alpha, j)
        encrypted_blocks.append(binary_to_text(cipher_bits))
        j += 1

    with open(output_file, 'wb') as f:
        for block in encrypted_blocks:
            f.write(bytes([ord(block[0]), ord(block[1])]))


encrypt_file("Text.md", "Cipher.md")