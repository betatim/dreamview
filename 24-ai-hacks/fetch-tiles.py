"""Fetching tiles from Bing"""
# 18/31554/48600
# z/x/y.png
#
import os
import requests
import shutil

import numpy as np

from skimage import io


def quad_key(x, y, zoom):
    x, y, zoom = int(x), int(y), int(zoom)
    quad_key = ''
    for i in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quad_key += str(digit)

    return quad_key


def bing_tile(quad_key):
    tile_url = ("http://t0.tiles.virtualearth.net/tiles/a{}.jpeg?"
                "g=5388".format(quad_key))
    return tile_url


def fetch_tile(x, y, z, prj_dir):
    x = str(x)
    y = str(y)
    z = str(z)
    no_imagery_img = io.imread("no-imagery.jpeg")
    tile_dir = os.path.join(prj_dir, x, y, z)
    os.makedirs(tile_dir, exist_ok=True)

    aerial_file = os.path.join(tile_dir, 'aerial.jpeg')
    aerial_file = os.path.join(prj_dir, '{x}_{y}_{z}.jpeg'.format(x=x,
                                                                  y=y,
                                                                  z=z))
    if not os.path.exists(aerial_file):
        qkey = quad_key(x, y, z)
        bing_url = bing_tile(qkey)

        r = requests.get(bing_url, stream=True)
        if r.status_code == 200:
            with open(aerial_file, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

            img = io.imread(aerial_file)
            if np.allclose(img, no_imagery_img):
                os.remove(aerial_file)
                return None

    return aerial_file


if __name__ == "__main__":
    N = 62
    X, Y = 63125, 97221

    for x in range(X, X + N):
        for y in range(Y, Y + N):
            fetch_tile(x, y, 18, '/tmp/24-ai-hacks/')
