
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(plaintext: str):
    """
    Hashes the plaintext password using bcrypt

    Args:
        plaintext: The password in plaintext

    Returns:
        The hashed password, including salt and algorithm information
    """
    return pwd_context.hash(plaintext)

def verify_password(plaintext: str, hashed: str) -> bool:
    """
    Checks the plaintext password against the provided hashed password

    Args:
        plaintext: The password as provided by the user
        hashed: The password as stored in the db

    Returns:
        True if the passwords match
    """

    return pwd_context.verify(plaintext, hashed)

def gen_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
        )
    public_key = private_key.public_key()

    return public_key, private_key

# Storing the keys
def store_keys(public_key, private_key, prefix):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
        )
    with open(f'{prefix}.private_key.pem', 'wb') as f:
        f.write(pem)

    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    with open(f'{prefix}.public_key.pem', 'wb') as f:
        f.write(pem)

def load_private_key(key_filename):
    with open(key_filename, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    return private_key

def load_public_key(key_filename):
    with open(key_filename, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
        )
    return public_key

# Encrypting and decrypting
def encrypt(message, public_key):
    enc = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    return enc

def decrypt(msg, private_key) -> str:
    dec = private_key.decrypt(
        msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return dec

if __name__ == '__main__':
    # A small tester:

    public_key, private_key = gen_keys()

    store_keys(public_key, private_key, prefix='test')

    private_key = load_private_key('test.private_key.pem')
    public_key = load_public_key('test.public_key.pem')

    enc = encrypt(b'encrypt some data', public_key)

    print(enc)

    print(decrypt(enc, private_key))

