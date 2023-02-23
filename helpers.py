import secp256k1
import base64

from cffi import FFI

# from Cryptodome.Cipher import AES
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


def get_shared_secret(privkey: str, pubkey: str):
    point = secp256k1.PublicKey(bytes.fromhex("02" + pubkey), True)
    return point.ecdh(bytes.fromhex(privkey), hashfn=copy_x)


def decrypt_message(encoded_message: str, encryption_key) -> str:
    encoded_data = encoded_message.split("?iv=")
    encoded_content, encoded_iv = encoded_data[0], encoded_data[1]

    iv = base64.b64decode(encoded_iv)
    cipher = Cipher(
        algorithms.AES(encryption_key), modes.CBC(iv)
    )
    encrypted_content = base64.b64decode(encoded_content)

    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_content) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_message) + unpadder.finalize()

    return unpadded_data.decode()

def decrypt(enc_text, encryption_key, iv):
    cipher = Cipher(algorithms.AES(encryption_key, modes.CBC(iv)))
    data = cipher.decrypt(enc_text)
    return data[: -(data[-1] if type(data[-1]) == int else ord(data[-1]))]

ffi = FFI()


@ffi.callback(
    "int (unsigned char *, const unsigned char *, const unsigned char *, void *)"
)
def copy_x(output, x32, y32, data):
    ffi.memmove(output, x32, 32)
    return 1
