from xex_mode import xex_decrypt
from helper_fc import binary_to_text, load_keys

def decrypt_file(input_file, output_file):
    key1, key2, tweak, alpha, _ = load_keys()
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    decrypted_blocks = []

    j = 0
    for i in range(0, len(content), 2):
        block = content[i:i+2]
        plain = xex_decrypt(block, key1, key2, tweak, alpha, j)
        decrypted_blocks.append(binary_to_text(plain))
        j += 1
    with open(output_file, 'w') as f:
        f.write("".join(decrypted_blocks))


decrypt_file("Cipher.txt", "Recovered.txt")