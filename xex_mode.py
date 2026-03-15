from s_aes import encrypt, decrypt, keyExpansion
from helper_fc import tweak_to_text, binary_to_text, gf_mult_16, gf_pow_16
#Cj​=EK1​(Pj​⊕Δj​)⊕Δj​
#Δj​=EK2​(T)⋅αj

#Tweak
def computeDelta(key2, tweak, alpha, j):
    key2 = keyExpansion(key2)
    tweak = tweak_to_text(tweak)
    T = int(encrypt(tweak ,key2), 2)
    alpha_pow_j = gf_pow_16(alpha, j)
    delta = gf_mult_16(T, alpha_pow_j)  
    return delta

#XEX-Encryption
def xex_encrypt(P, key1, key2, tweak, alpha, j):
    key1 = keyExpansion(key1)
    delta = computeDelta(key2, tweak, alpha, j)
    bin_P = (ord(P[0]) << 8) | ord(P[1])
    temp = f"{(bin_P ^ delta):016b}"
    C = int(encrypt(binary_to_text(temp), key1), 2) ^ delta
    return f"{C:016b}"

#XEX-Decryption
def xex_decrypt(C, key1, key2, tweak, alpha, j):
    key1 = keyExpansion(key1)
    delta = computeDelta(key2, tweak, alpha, j)
    bin_C = (ord(C[0]) << 8) | ord(C[1])
    temp = f"{(bin_C ^ delta):016b}"
    P = int(decrypt(binary_to_text(temp), key1), 2) ^ delta
    return f"{P:016b}"