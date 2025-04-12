from PIL import Image
import sys
import random
import math
import base64

def get_next_pixel(used, max):
     pos = math.floor(random.uniform(1, max))
     while(pos in used):
        pos = pos +1
        if pos > max:
            pos = 0
     return pos

def get_pixel_position(pixelNumber, x):
    return (pixelNumber % x) -1, math.floor(pixelNumber/x)

def split_RGB_on_values(rgb):
    even = []
    odd = []
    for idx,v in enumerate(rgb):
        if v % 2 == 0:
            even.append(idx)
        else:
            odd.append(idx)
    return even, odd

def build_new_pixel(rgb_list, wrong):
    needed_to_change = len(wrong)-1
    wrong_copy = wrong.copy()
    ret_val = rgb_list.copy()
    for i in range(0, needed_to_change):
        to_update = wrong_copy[i]
        wrong_copy.remove(to_update)
        old_value = rgb_list[to_update]
        if not old_value < 256:
            print(old_value)
        ret_val[to_update] = old_value + 1 if old_value < 255 else old_value -1
    return ret_val

def get_bit_value(rgb):
    even, _ = split_RGB_on_values(rgb)
    if len(even) > 1:
        return '1'
    else:
        return '0'

def write(im, text):
    used = []
    max = (im.size[0] * im.size[1]) -1
    pixels = im.load()

    for c in text:
        bitstring = bin(bytes(c, 'ascii')[0])[2:].zfill(8)
        for i in range(0,8):
            bit = bitstring[i]
            pixel = get_next_pixel(used,max)
            used.append(pixel)
            x,y = get_pixel_position(pixel, im.size[0])
            rgb = pixels[x, y]
            even, odd = split_RGB_on_values(rgb)
            rgb_list = list(rgb)
            if bit == '0':
                if len(odd) >= 2:
                    continue
                else:
                    rgb_list = build_new_pixel(rgb_list, even)
            else:
                if len(even) >= 2:
                    continue
                else:
                    rgb_list = build_new_pixel(rgb_list, odd)
            pixels[x,y] = tuple(rgb_list)
    # set next to 1 to mark end
    pixel = get_next_pixel(used, max)
    x,y = get_pixel_position(pixel, im.size[0])
    rgb = pixels[x, y]
    _, odd = split_RGB_on_values(rgb)
    rgb_list = list(rgb)
    if len(odd) >= 2:
        rgb_list = build_new_pixel(rgb_list, odd)
    pixels[x,y] = tuple(rgb_list)

def read(im):
    used = []
    max = (im.size[0] * im.size[1]) -1
    pixels = im.load()

    text = ""
    found_last = False
    while len(used) < max and not found_last:
        bitstring = ""
        for i in range(0,8):
            pixel = get_next_pixel(used, max)
            used.append(pixel)
            x,y = get_pixel_position(pixel, im.size[0])
            rgb = pixels[x, y]
            bit_value = get_bit_value(rgb)
            if (i == 0 and bit_value == '1'):
                found_last = True
                break
            bitstring = bitstring + bit_value
        if not found_last:
            text = text + chr(int(bitstring, 2))
    return base64.b64decode(text).decode('utf-8')

def handle_command(mode, key, file, text, im):
    random.seed(key)
    if mode == 'write':
        write(im, base64.b64encode(bytes(text, 'utf-8')).decode('utf-8'))
        newFileName = file.split('.')
        newFileName[0] = newFileName[0] + "_embeded"
        im.save('.'.join(newFileName))
    elif mode == 'read':
        print(read(im))


mode = sys.argv[1]
key = sys.argv[2]
file = sys.argv[3]
text = ' '.join(sys.argv[4:])
im = Image.open(file)

max = (im.size[0] * im.size[1]) -1

if max > len(base64.b64encode(bytes(text, 'utf-8')).decode('utf-8')) * 8:
    handle_command(mode, key, file, text, im)
else:
    print("image is to small for all that text")
