def xor(data, key):
    return bytearray(a^b for a, b in zip(*map(bytearray, [data, key])))

one_time_pad = b'#SECRETS#SECRETS#SECRETS#SECRETS#SECRETS#SECRETS#SECRETS#SECRETS#SECRETS#SECRETS#SECRETS#SECRETS#SECRETS#SECRETS'
plaintext = b'\x60\x3c\x21\x26\x30\x37\x31\x32\x48\x36\x37\x17\x3a\x20\x1c\x32\x51\x37\x15\x22\x20\x31\x60\x3c\x21\x26\x30\x37\x31\x32\x48\x36\x37\x17\x3a\x20\x1c\x32\x51\x37\x15\x22\x20\x31'

ciphertext = xor(plaintext, one_time_pad)
decrypted = xor(ciphertext, one_time_pad)
print(ciphertext)
print(decrypted)