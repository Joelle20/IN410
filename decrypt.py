from xex_mode import xex_decrypt, compute_T0
from helper_fc import load_keys, binary_to_text


def decrypt_file(input_file, output_file):
    key1, key2, tweak, alpha, _ = load_keys()

    T0 = compute_T0(key2, tweak)

    decrypted_blocks = []
    j = 0

    with open(input_file, 'rb') as f:
        content = f.read()

    for j, i in enumerate(range(0, len(content), 2)):
        block = chr(content[i]) + chr(content[i+1])
        plain = xex_decrypt(block, key1, T0, alpha, j)
        decrypted_blocks.append(binary_to_text(plain))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("".join(decrypted_blocks))


decrypt_file("Cipher.md", "Recovered.md")