#!/usr/bin/python

import urllib2
import os
import sys
from gmap_utils import *

import time
import random


def download_tiles(zoom, start_x, start_y, stop_x, stop_y, img_dir):

    user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1'
    headers = {'User-Agent': user_agent}

    for x in xrange(start_x, stop_x):
        for y in xrange(start_y, stop_y):

            url = "http://mt1.google.com/vt/lyrs=h@162000000&hl=en&x=%d&s=&y=%d&z=%d" % (
                x, y, zoom)
            if not os.path.exists(img_dir):
                os.mkdir(img_dir)

            filename = "%d_%d_%d.png" % (x, y, zoom)
            filename = os.path.join(img_dir, filename)

            if not os.path.exists(filename):

                bytes = None

                try:
                    req = urllib2.Request(url, data=None, headers=headers)
                    print(url)
                    response = urllib2.urlopen(req)
                    bytes = response.read()
                except Exception, e:
                    print "--", filename, "->", e
                    sys.exit(1)

                if bytes.startswith("<html>"):
                    print "-- forbidden", filename
                    sys.exit(1)

                print "-- saving", filename

                f = open(filename, 'wb')
                f.write(bytes)
                f.close()

                time.sleep(random.random())

if __name__ == "__main__":

    X, Y = 63125, 97221

    N = 62
    zoom = 18

    download_tiles(zoom, start_x=X - N, start_y=Y -
                   N, stop_x=X + N, stop_y=Y + N, img_dir='/tmp/gmap-tiles/')
