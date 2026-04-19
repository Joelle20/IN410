# S-AES Implementation with XEX Operation Mode and Cryptanalysis

A Python implementation of **XTS-AES** (XEX-based Tweaked CodeBook mode with ciphertext Stealing) built on top of a simplified **S-AES** (Simplified AES) cipher. The project includes full encryption/decryption of text files and a **Chosen Plaintext Attack (CPA)** to recover unknown keys.

---

## Project Structure

```
├── s_aes.py        # Simplified AES cipher (encrypt / decrypt)
├── xex_mode.py     # XEX mode layer
├── helper_fc.py    # Shared utilities (GF arithmetic, binary/text conversion, key loader)
├── encrypt.py      # Encrypts file Text.txt → Cipher.txt
├── decrypt.py      # Decrypts file Cipher.txt → Recovered.txt
├── attack.py       # Chosen Plaintext Attack to recover key1, T0, and alpha
└── keys.json       # Key configuration file
```

---

## How It Works

### S-AES (`s_aes.py`)
A 16-bit block cipher that mimics full AES with a reduced state size. It operates on a 2×2 nibble state and performs:
- **SubNibbles** — non-linear substitution using a 4×4 S-Box
- **ShiftRows** — cyclic row shift
- **MixColumns** — linear mixing over GF(2⁴)
- **AddRoundKey** — XOR with round key

Key expansion generates 3 round keys (K0, K1, K2) from a 16-bit master key.

### XEX Mode (`xex_mode.py`)
Wraps S-AES in XEX (XOR-Encrypt-XOR) mode for block-level encryption:

```
delta_j = T0 * alpha^j (in GF(2^16))
C = E(P ^ delta_j, key1) ^ delta_j
```

Where `T0 = E_key2(tweak)`.

### File Encryption / Decryption
- Spaces are stripped from plaintext before encryption
- Odd-length content is padded with the character defined in `keys.json`
- Cipher file is written in **binary mode** to prevent UTF-8 from expanding certain cipher bytes into multi-byte sequences, which would corrupt block alignment on read-back
- Decrypted output is written as a plain **UTF-8 text file**

## GF Arithmetic

| Function | Field | Irreducible Polynomial | Used In |
|---|---|---|---|
| `gf_mult(a, b)` | GF(2⁴) | `x⁴ + x + 1` (`0x13`) | S-AES MixColumns |
| `gf_mult_16(a, b)` | GF(2¹⁶) | `x¹⁶ + x¹² + x⁵ + 1` (`0x1021`) | XEX delta computation |
| `gf_pow_16(base, exp)` | GF(2¹⁶) | same as above | XEX delta computation |
---

## Configuration — `keys.json`

| Field | Description |
|---|---|
| `key1` | 16-bit S-AES encryption key (hex) |
| `key2` | 16-bit key used to encrypt the tweak (hex) |
| `tweak` | 16-bit tweak value for XEX mode (hex) |
| `alpha` | Primitive element of GF(2¹⁶) for delta computation (hex) |
| `padding` | Single character appended if plaintext length is odd |

---

## Usage

### Encrypt a file
Place your plaintext in `Text.md`, then run:
```bash
python encrypt.py
```
Output is written to `Cipher.md` (binary file).

### Decrypt a file
```bash
python decrypt.py
```
Output is written to `Recovered.md`.

---

## Cryptanalysis — Chosen Plaintext Attack (`attack.py`)

A **Chosen Plaintext Attack (CPA)** that recovers `key1`, `T0`, and `alpha` without knowing any of them in advance. The attacker only needs access to the encryption oracle `xex_encrypt(pt, j)` and two known plaintext-ciphertext pairs at `j=1` and `j=2`.

### Mathematical Insight

At block index `j=0`, `alpha^0 = 1` always, so `delta_0 = T0`. The XEX equation simplifies to:

```
C = E(P ^ T0, key1) ^ T0
```

If we query the oracle with plaintext `P = x` for every possible `x`, then when `x = T0`:

```
input to E = x ^ T0 = 0
→ E(0, key1) = C_x ^ x
```

This fully decouples `key1` from `T0`, reducing the search from 2³² to 2¹⁶.

### Attack Steps

**Step 1 — Build `table_zero`** (done once, 2¹⁶ encryptions)
Precompute `E(0x0000, key)` for every possible key and store as `output → key`.

**Step 2 — Query the oracle** (2¹⁶ queries)
Encrypt all 65536 possible 2-character plaintexts at `j=0`. Save responses as `x → ciphertext`.

**Step 3 — Find candidates**
For each oracle response, compute `target = C_x ^ x` and look it up in `table_zero`. A hit means `x = T0` and the matched key is `key1`.

**Step 4 — Filter candidates**
Build a second table `table_one` for input `0x0001`. For each candidate `(key1, T0)`, verify using the oracle response at plaintext `T0 ^ 1`. This cross-check eliminates false positives, typically reducing the len of raw candidates. 

**Step 5 — Solve for alpha**
With `key1` and `T0` known, iterate all possible alpha values (2¹⁶) and check against the known pair at `j=1`. Verify the result against the known pair at `j=2`.

### Complexity

| Step | Description | Cost |
|---|---|---|
| 1 | Precompute `E(0, key)` for all keys | 2¹⁶ encryptions |
| 2 | Oracle queries at j=0 | 2¹⁶ queries |
| 3 | Table lookups | 2¹⁶ × O(1) |
| 4 | Filter with second table | 2¹⁶ encryptions |
| 5 | Solve alpha + verify | ≤ 2¹⁶ checks |

**Total: ~4 × 2¹⁶ ≈ 260,000 operations.**

### Running the Attack

```bash
python attack.py
```

Expected output:
```
CHOSEN PLAINTEXT ATTACK
==========================
[1] Building table for E(0, key)...
[2] Querying xex_encrypt...
[3] Finding (key1, T0) candidates...
        Candidates found: ~41000
[4] Filtering candidates...
        Remaining candidates: ~2
[5] Searching for alpha...

[SUCCESS]
key1  = 0xA73B
T0    = 0xXXXX (= encrypt(tweak, key2))
alpha = 0x0002
```

---
## Dependencies

- Python 3.x (no third-party packages required)
- All modules are pure Python using only the standard library
