from s_aes import encrypt, decrypt, keyExpansion
from helper_fc import gf_mult_16, gf_pow_16, binary_to_text, load_keys

def compute_T0(key2, tweak):
    key2 = keyExpansion(key2)
    tweak_bin = f"{int(tweak):016b}"
    return int(encrypt(tweak_bin, key2), 2)

def computeDelta(T0, alpha, j):
    alpha_pow = gf_pow_16(alpha, j)
    return gf_mult_16(T0, alpha_pow)

def xex_encrypt_file(P, key1, T0, alpha, j):
    key1 = keyExpansion(key1)
    delta = computeDelta(T0, alpha, j)
    bin_P = (ord(P[0]) << 8) | ord(P[1])
    temp = f"{(bin_P ^ delta):016b}"
    C = int(encrypt(binary_to_text(temp), key1), 2) ^ delta
    return f"{C:016b}"


def xex_decrypt_file(C, key1, T0, alpha, j):
    key1 = keyExpansion(key1)
    delta = computeDelta(T0, alpha, j)
    bin_C = (ord(C[0]) << 8) | ord(C[1])
    temp = f"{(bin_C ^ delta):016b}"
    P = int(decrypt(binary_to_text(temp), key1), 2) ^ delta
    return f"{P:016b}"


def xex_encrypt(plaintext, j):
    key1, key2, tweak, alpha, _ = load_keys()
    T0 = compute_T0(key2, tweak)
    result = xex_encrypt_file(plaintext, key1, T0, alpha, j)
    return binary_to_text(result)