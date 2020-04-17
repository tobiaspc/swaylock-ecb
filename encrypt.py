#!/usr/bin/env python3
from PIL import Image
from Crypto.Cipher import AES
from Crypto import Random
from argparse import ArgumentParser

key = Random.new().read(AES.key_size[0])
mode = AES.MODE_ECB
aes = AES.new(key, mode)

def encrypt_image(imagepath, key):
    image = Image.open(imagepath)
    image_array = image.tobytes()

    padding_length = AES.block_size - len(image_array) % AES.block_size
    image_array += bytes(padding_length * ".", "UTF-8") # Just an arbitrary padding byte

    encrypted_image = aes.encrypt(image_array)
    encrypted_image = encrypted_image[:-padding_length]

    return Image.frombytes("RGB", image.size, encrypted_image, "raw", "RGB")

if __name__ == "__main__":
    parser = ArgumentParser(description="Encrypt images with AES ECB")

    parser.add_argument('-i','--input', nargs='+', help='<Required> List of input files', required=True)
    parser.add_argument('-o','--output', nargs='+', help='<Required> List of output files', required=True)
    
    args = parser.parse_args()
    
    for i in range(0, len(args.input)):
        encrypt_image(args.input[i], key).save(args.output[i])

