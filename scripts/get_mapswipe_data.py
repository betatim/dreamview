import shutil
import requests
import json
import os
import sys

import numpy as np


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


def fetch_tiles(project_id, n_tiles=2000):
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

    for n,tile in enumerate(prj_info):
        if not n % 10:
            print("fetch %i tiles" % n)
        if n > n_tiles:
            break

        klass = str(tile['decision']) # 1 = yes, 2 = maybe, 3 = bad image

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

        XXX = """
        if yes/total >= 0.5:
            klass = "1"
        elif maybe/total >= 0.5:
            klass = "2"
        elif bad/total >= 0.5 or yes == maybe == bad:
            klass = "3"
        else:
            print(yes, maybe, bad)
            import pdb
            pdb.set_trace()"""

        x, y, z = tile['task_x'], tile['task_y'], tile['task_z']

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


if __name__ == "__main__":
    project_id = sys.argv[1]

    fetch_tiles(project_id)
