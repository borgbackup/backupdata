Tools for backup scalability testing
====================================

I made this to test scalability for borgbackup, but maybe you find it useful
for testing other stuff, too.

mkdata.py
---------

Realistically testing a deduplication backup software with a lot of data isn't
easy if you do not have a lot of such data.

If you need to create such data, you can't just duplicate existing data (the
backup tool would just deduplicate it and not create a lot of output data).
Also, just fetching data from /dev/urandom is rather slow (and the data is not
at all "realistic", because it is too random).

The solution is to start from a set of real files (maybe 1-2GB in size), but
to modify each copy slightly (and repeatedly, so there are not even longer
duplicate chunks inside the files) by inserting some bytes derived from a
counter.

Please note that due to this, all output files are "corrupt" copies and
only intended as test data and expected to be thrown away after the test.
The input files are not modified on disk.

This tool expects some data in the SRC directory, it could look like
this, for example (test data is not included, please use your own data):

::

    234M  testdata/bin     # linux executable binaries
    245M  testdata/jpg     # photos
    101M  testdata/ogg     # music
    4.0K  testdata/sparse  # 1x 1GB empty sparse file, name must be "sparse"
    259M  testdata/src_txt # source code, lots of text files
    151M  testdata/tgz     # 1x tar.gz file


Make sure all the SRC data fits into memory as it will be read into and kept
in RAM for better performance.

The tool creates N (modified) copies of this data set in directories named
0 .. N inside the DST directory.

The copies of the empty "sparse" file will also be created as empty sparse
files and they won't be modified. This can be used to test extreme
deduplication (or handling of sparse input files) by the tested backup tool.

