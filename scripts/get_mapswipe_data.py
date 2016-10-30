import shutil
import requests
import json
import os
import sys
import random

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


def fetch_tile(x, y, z, klass, prj_dir):
    no_imagery_img = io.imread("no-imagery.jpeg")
    tile_dir = os.path.join(prj_dir, klass, x, y, z)
    os.makedirs(tile_dir, exist_ok=True)

    aerial_file = os.path.join(tile_dir, 'aerial.jpeg')
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


def fetch_tiles(project_id, n_tiles=4000, seed=1):
    rng = random.Random(seed)

    prj_dir = "/tmp/mapswipe/project-%s" % project_id
    os.makedirs(prj_dir, exist_ok=True)

    if not os.path.exists('info.json'):
        url = 'http://api.mapswipe.org/projects/%s.json' % (project_id)
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(os.path.join(prj_dir, 'info.json'), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    print("start fetching tiles")

    with open(os.path.join(prj_dir, 'info.json')) as f:
        prj_info = json.load(f)

    # 1 = yes, 2 = maybe, 3 = bad image, 4 = perfect tie, 5 = boring
    for n,tile in enumerate(prj_info):
        if not n % 10:
            print("fetched %i tiles" % n)
        if n > n_tiles:
            break

        klass = str(tile['decision'])

        yes = tile['yes_count']
        maybe = tile['maybe_count']
        bad = tile['bad_imagery_count']
        total = yes + maybe + bad

        # by putting bad and maybe before yes we prefer those in case of ties
        classes = ['2', '3', '1']
        if yes == maybe == bad:
            klass = "4"
        else:
            klass = classes[np.argmax([maybe, bad, yes])]

        x, y, z = tile['task_x'], tile['task_y'], tile['task_z']

        fetch_tile(x, y, z, klass, prj_dir)

    # now fetch "boring" tiles
    min_x, max_x = (min(int(t['task_x']) for t in prj_info),
                    max(int(t['task_x']) for t in prj_info))
    min_y, max_y = (min(int(t['task_y']) for t in prj_info),
                    max(int(t['task_y']) for t in prj_info))

    # tiles which we know aren't boring
    good_pairs = set((int(t['task_x']), int(t['task_y'])) for t in prj_info)
    # boring tiles we already downloaded
    seen_pairs = set()
    for n in range(n_tiles):
        if not n % 10:
            print("fetched %i boring tiles" % n)

        x = rng.randint(min_x, max_x)
        y = rng.randint(min_y, max_y)

        while (x,y) in good_pairs or (x,y) in seen_pairs:
            x = rng.randint(min_x, max_x)
            y = rng.randint(min_y, max_y)

        seen_pairs.add((x, y))
        fetch_tile(str(x), str(y), "18", "5", prj_dir)


if __name__ == "__main__":
    project_id = sys.argv[1]

    fetch_tiles(project_id)
