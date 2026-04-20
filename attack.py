from s_aes import encrypt, keyExpansion
from helper_fc import gf_mult_16, gf_pow_16, binary_to_text, to_int16
from xex_mode import xex_encrypt

def attack(xex_encrypt, pair_j1, pair_j2):

    P1, C1 = pair_j1
    P2, C2 = pair_j2

    P1_int = to_int16(P1[0], P1[1])
    C1_int = to_int16(C1[0], C1[1])
    P2_int = to_int16(P2[0], P2[1])
    C2_int = to_int16(C2[0], C2[1])

    #1-Build table E(0, key)
    print("[1] Building table for E(0, key)...")

    expanded_keys = [keyExpansion(k) for k in range(0x10000)]

    zero_input = binary_to_text(f"{0:016b}")
    table_zero = {}   # output → key

    for key in range(0x10000):
        result = int(encrypt(zero_input, expanded_keys[key]), 2)
        table_zero[result] = key

    #2-Query xex_encrypt
    print("[2] Querying oracle...") #oracle is a black box function 

    xex_encrypt_data = {}   #save x → ciphertext

    for x in range(0x10000):
        pt = chr(x >> 8) + chr(x & 0xFF) #convert int to 2 chars text
        ct = xex_encrypt(pt, j=0)
        xex_encrypt_data[x] = to_int16(ct[0], ct[1])

    #3-Find candidates
    print("[3] Finding (key1, T0) candidates...")

    candidates = []
    for guess_T0, cipher_val in xex_encrypt_data.items():
        target = cipher_val ^ guess_T0
        if target in table_zero:
            key1 = table_zero[target]
            candidates.append((key1, guess_T0))

    print(f"\tCandidates found: {len(candidates)}")


    #4-Filter candidates
    print("[4] Filtering candidates...")

    one_input = binary_to_text(f"{1:016b}")
    table_one = {}
    for key in range(0x10000):
        result = int(encrypt(one_input, expanded_keys[key]), 2)
        table_one[result] = key

    filtered = []
    for key1, T0 in candidates:
        x = T0 ^ 1
        cipher_val = xex_encrypt_data.get(x)
        if cipher_val is None:
            continue

        target = cipher_val ^ T0
        if target in table_one and table_one[target] == key1:
            filtered.append((key1, T0))

    print(f"\tRemaining candidates: {len(filtered)}")

    #5-Find alpha
    print("[5] Searching for alpha...")

    for key1, T0 in filtered:
        key_exp = expanded_keys[key1]
        for alpha in range(1, 0x10000):
            delta1 = gf_mult_16(T0, alpha)
            inp = binary_to_text(f"{(P1_int ^ delta1):016b}")
            test = int(encrypt(inp, key_exp), 2) ^ delta1
            if test == C1_int:
                #verify using second pair
                delta2 = gf_mult_16(T0, gf_pow_16(alpha, 2))
                inp = binary_to_text(f"{(P2_int ^ delta2):016b}")
                test2 = int(encrypt(inp, key_exp), 2) ^ delta2
                if test2 == C2_int:
                    print("\n[SUCCESS]")
                    print(f"key1  = 0x{key1:04X}")
                    print(f"T0    = 0x{T0:04X} (= encrypt(tweak, key2))")
                    print(f"alpha = 0x{alpha:04X}")

                    return key1, T0, alpha

    print("Attack failed.")
    return None




if __name__ == "__main__":
    P1 = "24"
    C1 = xex_encrypt(P1, j=1)

    P2 = "62"
    C2 = xex_encrypt(P2, j=2)

    print("CHOSEN PLAINTEXT ATTACK")
    print("==========================")

    attack(xex_encrypt, (P1, C1), (P2, C2))