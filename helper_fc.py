import json

def binary_to_text(bin_str):
    first_byte = bin_str[:8]
    second_byte = bin_str[8:]
    
    char1 = chr(int(first_byte, 2))
    char2 = chr(int(second_byte, 2))
    
    return char1 + char2

def text_to_binary(text):
    return "".join(format(ord(c), '08b') for c in text)

def tweak_to_text(tweak):
    first_char = chr((tweak >> 8) & 0xFF)
    second_char = chr(tweak & 0xFF)
    
    return first_char + second_char

#GF mult
def gf_mult(a, b):
    p = 0
    for _ in range(4):
        if b & 1:
            p ^= a
        a <<= 1
        if a & 0x10:
            a ^= 0b10011
        b >>= 1
    return p & 0xF

def gf_mult_16(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        if a & 0x10000:          
            a ^= 0x1021            
        b >>= 1
    return result & 0xFFFF   

def gf_pow_16(base, exponent):
    result = 1
    while exponent > 0:
        if exponent & 1:
            result = gf_mult_16(result, base)
        base = gf_mult_16(base, base)
        exponent >>= 1
    return result   

def load_keys():
    with open("keys.json", "r") as f:
        keys = json.load(f)
    key1 = int(keys["key1"], 16)
    key2 = int(keys["key2"], 16)
    tweak = int(keys["tweak"], 16)
    alpha = int(keys["alpha"], 16)
    pad = keys["padding"]
    return key1, key2, tweak, alpha, pad
