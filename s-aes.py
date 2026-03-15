#Initialize constants

SBOX = [
    [0x9, 0x4, 0xA, 0xB],
    [0xD, 0x1, 0x8, 0x5],
    [0x6, 0x2, 0x0, 0x3],
    [0xC, 0xE, 0xF, 0x7]
]

INV_SBOX = [
    [0xA, 0x5, 0x9, 0xB],
    [0x1, 0x7, 0x8, 0xF],
    [0x6, 0x0, 0x2, 0x3],
    [0xC, 0x4, 0xD, 0xE]
]

MC = [
    [0x1, 0x4],
    [0x4, 0x1]
]

INV_MC = [
    [0x9, 0x2],
    [0x2, 0x9]
]

RCON1 = 0x80
RCON2 = 0x30


#Create State
def createState(text):
    hex_notation = [f"{ord(c):02x}" for c in text]
    
    n0 = int(hex_notation[0][0], 16) 
    n1 = int(hex_notation[0][1], 16)
    n2 = int(hex_notation[1][0], 16)
    n3 = int(hex_notation[1][1], 16)
    
    return [
        [n0, n2],
        [n1, n3]
    ]

#Helper function
def binary_to_text(bin_str):
    first_byte = bin_str[:8]
    second_byte = bin_str[8:]
    
    char1 = chr(int(first_byte, 2))
    char2 = chr(int(second_byte, 2))
    
    return char1 + char2

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

#AddRoundKey
def addRoundKey(state, key):
    flatState = (state[0][0] << 12) | (state[1][0] << 8) | (state[0][1] << 4)  | (state[1][1])
    res = flatState ^ key
    return [
        [(res >> 12) & 0xF, (res >> 4) & 0xF],
        [(res >> 8) & 0xF, (res) & 0xF]
    ]

#SubNibbles
def subNib(b):
    row = (b & 0xC) >> 2
    col = b & 0x3
    return SBOX[row][col]

def subNibbles(state):
    new_state = [[0, 0], [0, 0]]
    for i in range(2):
        for j in range(2):
            new_state[i][j] = subNib(state[i][j])
    return new_state

#InvSubNibbles
def invSubNib(b):
    row = (b & 0xC) >> 2
    col = b & 0x3
    return INV_SBOX[row][col]

def invSubNibbles(state):
    new_state = [[0, 0], [0, 0]]
    for i in range(2):
        for j in range(2):
            new_state[i][j] = invSubNib(state[i][j])
    return new_state
    

#ShiftRows
def shiftRows(state):
    return [
        [state[0][0], state[0][1]], 
        [state[1][1], state[1][0]]  
    ]

#MixColumns
def mixColumns(state):
    n0, n2 = state[0]
    n1, n3 = state[1]

    m0 = n0 ^ gf_mult(4, n1)
    m1 = n1 ^ gf_mult(4, n0)
    m2 = n2 ^ gf_mult(4, n3)
    m3 = n3 ^ gf_mult(4, n2)

    return [[m0, m2], [m1, m3]]

#InvMixColumns
def invMixColumns(state):
    n0, n2 = state[0]
    n1, n3 = state[1]

    m0 = gf_mult(9, n0) ^ gf_mult(2, n1)
    m1 = gf_mult(2, n0) ^ gf_mult(9, n1)
    m2 = gf_mult(9, n2) ^ gf_mult(2, n3)
    m3 = gf_mult(2, n2) ^ gf_mult(9, n3)

    return [[m0, m2], [m1, m3]]


#Key Generation

def rotNib(b):
    return ((b << 4) | (b >> 4)) & 0xFF

def subNibByte(b):
    nib1 = subNib((b >> 4) & 0xF)
    nib2 = subNib(b & 0xF)
    return (nib1 << 4) | nib2


def keyExpansion(key):
    w = [0] * 6

    w[0] = (key >> 8) & 0xFF
    w[1] = key & 0xFF

    w[2] = w[0] ^ subNibByte(rotNib(w[1])) ^ RCON1
    w[3] = w[1] ^ w[2]

    w[4] = w[2] ^ subNibByte(rotNib(w[3])) ^ RCON2
    w[5] = w[3] ^ w[4]

    k0 = (w[0] << 8) | w[1]
    k1 = (w[2] << 8) | w[3]
    k2 = (w[4] << 8) | w[5]

    return k0, k1, k2


#Encryption
def encrypt(plaintext, key):
    state = createState(plaintext)

    state = addRoundKey(state, key[0])

    state = mixColumns(shiftRows(subNibbles(state)))
    state = addRoundKey(state, key[1])

    state = shiftRows(subNibbles(state))
    state = addRoundKey(state, key[2])

    cipher = (state[0][0] << 12) | (state[1][0] << 8) | (state[0][1] << 4)  | (state[1][1])

    return f"{cipher:016b}"

#Decryption
def decrypt(ciphertext, key):
    state = createState(ciphertext)

    state = addRoundKey(state, key[2])

    state = addRoundKey(invSubNibbles(shiftRows(state)), key[1])
    state = invMixColumns(state)

    state = invSubNibbles(shiftRows(state))
    state = addRoundKey(state, key[0])

    plaintext = (state[0][0] << 12) | (state[1][0] << 8) | (state[0][1] << 4)  | (state[1][1])

    return f"{plaintext:016b}"

#test
plaintext = "ok"
bin_plaintext = "".join(format(ord(c), '08b') for c in plaintext)
print(f"Plain Text: {bin_plaintext} \n")
key0 = 0b1010011100111011
key = keyExpansion(key0)
for i, k in enumerate(key):
    print(f"Key{i}: {k}")
cipher = encrypt(plaintext, key)
print(f"\nCipher Text: {cipher}")
ciphertext = binary_to_text(cipher)
plain = decrypt(ciphertext, key)
print(f"Recovered Plain Text: {plain}")

