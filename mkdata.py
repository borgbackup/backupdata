"""
Create lots of test data for backup scalability testing.

Usage:
- edit the constant at the top of the file as you need them
- run it with: python3 mkdata.py

Copyright 2015 Thomas Waldmann <tw@waldmann-edv.de>
Licensed under the BSD 3-clause license.
"""

import os
import struct

# how often do you want the test data to be duplicated?
# it won't be exact duplicates to avoid deduplication.
N = 5000

# each BLK_SIZE bytes (or, if file is smaller, in the middle of the file),
# we insert a counter into the output file to avoid creating a duplicate.
BLK_SIZE = 65536

# arrange some test src data in this directory
# make sure it fits into RAM as it will all be read into RAM, except the
# "sparse" file. you may put 1 sparse file in there, name it "sparse".
SRC = 'testdata'

# where we put the output data, make sure there is enough space.
DST = 'lotsofspace'


def read_testdata(src):
    """read all test data into memory"""
    data = {}  # relname -> binary file content
    size = 0
    src_len = len(src)
    for root, dirs, files in os.walk(src, topdown=False):
        for name in files:
            fn = os.path.join(root, name)
            relname = fn[src_len + 1:]
            if relname.endswith('sparse'):
                data[relname] = os.path.getsize(fn)
            else:
                with open(fn, 'rb') as f:
                    contents = f.read()
                    size += len(contents)
                    data[relname] = contents
    return data, size


def modify_write_data(dst, data, i, blk_size=BLK_SIZE):
    """create a modified copy of the test data"""
    modifier = struct.pack('l', i)
    dst = dst.rstrip(os.path.sep) + os.path.sep + str(i) + os.path.sep
    for relname, contents in data.items():
        fn = dst + relname
        base_dir = os.path.dirname(fn)
        os.makedirs(base_dir, exist_ok=True)
        if relname.endswith('sparse'):
            with open(fn, 'wb') as f:
                size = contents
                f.seek(size)
                f.write(b'!')
        else:
            with open(fn, 'wb') as f:
                pos = 0
                content_len = len(contents)
                # make sure we also modify short files:
                if content_len < blk_size:
                    _blk_size = int(content_len / 2)
                else:
                    _blk_size = blk_size
                while pos < content_len:
                    f.write(contents[pos:pos + _blk_size])
                    f.write(modifier)
                    pos += _blk_size


def main(src, dst, n):
    data, size = read_testdata(src)
    print("Size of input data: %d" % size)
    print("Creating %d modified copies of this:" % n)
    for i in range(0, n):
        print("Writing %d of %d..." % (i+1, n))
        modify_write_data(dst, data, i)


if __name__ == '__main__':
    main(SRC, DST, N)

