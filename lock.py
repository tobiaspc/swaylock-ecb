#!/usr/bin/env python3
# Version 0.2

from PIL import Image
from Crypto.Cipher import AES
from Crypto import Random
from argparse import ArgumentParser
import subprocess
import shlex
import os, sys
from timeit import default_timer as timer
import tempfile
import json 
import time

# Generate random AES key
key = Random.new().read(AES.key_size[0])
mode = AES.MODE_ECB
aes = AES.new(key, mode)

path = os.path.dirname(sys.argv[0])
icon = path + "/icons/lock.png"

# Setup parameters
swaylock_cmd = "swaylock"
swaylock_params = ["-f", "-k", "-e", "--indicator-radius", "85"]
output_params = []

# Encrypts binary data
def encrypt_image(image_array, width, height):
    padding_length = AES.block_size - len(image_array) % AES.block_size
    image_array += bytes(padding_length * ".", "UTF-8") # Just an arbitrary padding byte

    encrypted_array = aes.encrypt(image_array)
    return encrypted_array[:-padding_length]

# Returns a list of active outputs
def get_outputs():

    # Old jq code, is very slow compared to native python (~50ms)
    # command="swaymsg -t get_outputs | jq -r '.[]  | select(.active == true) | .name'"
    command="swaymsg -t get_outputs"
    
    active_outputs = []
    
    process = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
    data = process.communicate()[0]
    data = json.loads(data)

    # Select outputs that are active
    for item in data:
        if item.get('type') == 'output' and item.get('active'):
                active_outputs.append(item['name'])

    return active_outputs

# Takes a screenshot from the specified output and returns the raw image data in PPM format
def take_screenshot(output):
    command = "grim -t ppm -o " + output + " -"

    process = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.communicate()[0]

# Pixelates a image and writes it to the specified filename
def pixelate(screenshot, filename):
    command = "convert '-[10%]' -sample '1000%' -level '10%,90%' " + icon + " -gravity center -composite " + filename

    process = subprocess.Popen(command,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.communicate(input=screenshot)[0]

# Executes swaylock with the given parameters
def swaylock(swaylock_params, output_params):
    command = swaylock_cmd + " " + " ".join(swaylock_params) + " " + " ".join(output_params)
    process = subprocess.Popen(command,shell=True)

# Prints timing debug output
def time_debug(string, start, end, debug):
    if not debug:
        return

    print("Time " + string + ": %.f ms" % (1000 * (end - start)))


# Entry point
if __name__ == "__main__":
    parser = ArgumentParser(description="Encrypt images with AES ECB")

    parser.add_argument('-d','--debug', help='Debug output',action="store_true")
    args = parser.parse_args()

    start = timer()
    fullstart = start
    
    outputs = get_outputs()

    end = timer()
    time_debug("Output detect", start, end, args.debug)
    start = timer()

    output_params = []
    temp_files = []

    for i in range(0,len(outputs)):

        # Take screenshot
        screenshot = take_screenshot(outputs[i])

        end = timer()
        time_debug(outputs[i] + " screenshot", start, end, args.debug)
        start = timer()

        # Split into header and data
        header = screenshot.split(b'\n',maxsplit=3)[0:3]
        data = screenshot.split(b'\n',maxsplit=3)[3:]

        # Get size
        width, height = header[1].decode('UTF-8').split(' ')
        width = int(width)
        height = int(height)

        # Encrypt data
        data = encrypt_image(data[0], width, height)

        end = timer()
        time_debug("encrypt " + outputs[i], start, end, args.debug)
        start = timer()

        # Merge header and data again
        data_crypt = header[0] + b"\n" + header[1] + b"\n" + header[2] + b"\n" + data
        
        # Generate filename
        temp_file = tempfile.NamedTemporaryFile(prefix="swaylock-ecb-" + outputs[i] +"-", suffix=".ppm")
        name = temp_file.name
        temp_files.append(name)
        temp_file.close()

        # Pixelate, add lock icon, write to disk
        pixelate(data_crypt, name)

        end = timer()
        time_debug("pixelate and write " + outputs[i], start, end, args.debug)
        start = timer()
        
        # Prepare parameter for swaylock
        output_params.append("-i " + outputs[i] + ":" + name)

    end = timer()
    time_debug("total", fullstart, end, args.debug)
    
    # Execute swaylock
    swaylock(swaylock_params, output_params)

    # Delete output files after 1s, since swaylock needs time to load the images
    time.sleep(1)
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
        else:
            print("Error: Could not delete temporary file: " + file) 

