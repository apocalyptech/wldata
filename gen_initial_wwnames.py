#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:

# Wonderlands Data Processing Scripts
# Copyright (C) 2021-2022 CJ Kucera
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the development team nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL CJ KUCERA BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import re
import sys
import struct
import subprocess

# Script used to generate an initial `wwnames.txt` file to use along with the
# wwiser project, for making sense of audio banks in the Wonderlands data.
#
#    https://github.com/bnnm/wwiser
#    https://github.com/bnnm/wwiser-utils
#
# The generated list here, by nature, has an awful lot of cruft in it which
# isn't actually useful.  To re-generate the .txt file during `wwiser.py`:
#
#    wwiser.py -g -sl *.bnk
#
# I was worried that CPython might be annoyingly slow for this, but for BL3
# on my system, this finishes in ~26secs, compared to ~18 for PyPy3.  I didn't
# time it exactly for WL but it's similarly fast.  So: whatever.

###
### Config vars!
###

# Unlike in BL3, Wonderlands doesn't have an OSX version, so we can't make
# use of an unstripped OSX binary to provide some extra strings for us.
# Instead, I just dumped the memory of a running Wonderlands process and
# ran that through `strings` a few times with various encodings, concatenated
# it all together, stripped out anything that wasn't primarily alphanumeric,
# and we'll se that as a base.
binary_strings = 'final-binaries-strings.txt'

# Data directory to find a fully-extracted WL data set
data_dir = 'extracted'

# Hash collisions!  Uncomment the ones you want to prune out.  Organizing these
# by pairs, so that the ones colliding are obvious.  The wwiser process will
# output these as it processes, with lines like:
#
#    names: alt hashnames (using old), old=foo vs new=bar
collisions_to_remove = set([

    'BankInventoryList',
    #'OW_Mis_Blueprints_HammerStrike',
    
    #'Crea_VorcanarBoss_FireBeam_Start',
    'n39l',

    #'Wep_Crossbow_AR',
    'v58v',

    #'Crea_Mushroom_Voc_Magic_Death_Shock',
    'Wa3ac',

    #'Crea_Mushroom_Voc_Zombie_Spawn_WalkOut',
    'LicP',
    'lIcp',

    ])

# Filename to write out to
output_filename = 'wwnames-firstpass.txt'

###
### And now the app
###

def read_int(df):
    return struct.unpack('<i', df.read(4))[0]

def read_str(df):
    strlen = read_int(df)
    # The length includes a null byte at the end
    # Also decoding to latin1 may not always be the right thing
    # to do, though so far I've not seen anything other than ASCII
    if strlen < 0:
        strlen = abs(strlen)
        return df.read(strlen*2)[:-2].decode('utf_16_le')
    else:
        return df.read(strlen)[:-1].decode('latin1')

# Our set of potential strings
potential_strings = set()

# Grab strings from memory dump
if os.path.exists(binary_strings):
    print(f'Grabbing main binary strings from: {binary_strings}')
    with open(binary_strings) as df:
        for line in df:
            potential_strings.add(line.strip())
else:
    print(f'WARNING: {binary_strings} not found, skipping main binary import')

# Walk the object filesystem
print(f'Walking object filesystem from: {data_dir}')
processed = 0
for dirname, dirnames, filenames in os.walk(data_dir):
    for filename in filenames:
        if filename.endswith('.uasset') or filename.endswith('.umap'):

            # Add in our path components
            # We're doing this because many of the object names show up in there, but
            # with their first underscore-delimited part removed.  This is the case
            # at least for `WE_*` objects and `WwiseBank_*` objects.  This is probably
            # a bit unnecessary now that we're reading in the name catalog from the
            # objects directly -- these names probably show up in there anyway -- but
            # compared reading the data it's super quick to do, so whatever.
            parts = filename.rsplit('.', 1)[0].split('_')
            for i in range(len(parts)):
                potential_strings.add('_'.join(parts[i:]))

            # Add in everything from the object's name index
            with open(os.path.join(dirname, filename), 'rb') as df:

                # Blah, initial header stuff
                df.read(20)

                # Some number of FCustomVersion
                length = read_int(df)
                for _ in range(length):
                    df.read(20)

                total_header_size = read_int(df)
                folder_name = read_str(df)
                # package_flags is actually a uint, but whatever.
                package_flags = read_int(df)
                name_count = read_int(df)
                name_offset = read_int(df)

                # Now we've read enough to skip right to the name catalog
                df.seek(name_offset)
                for _ in range(name_count):
                    name = read_str(df)
                    if '/' not in name:
                        potential_strings.add(name)
                    # This is actually two shorts
                    read_int(df)

            # Report
            processed += 1
            if processed % 1000 == 0:
                print(f' - Processed {processed} files...')

# Process our known collisions
for collision in collisions_to_remove:
    potential_strings.remove(collision)

with open(output_filename, 'w') as df:
    print(f'Writing out to: {output_filename}')
    print('# Wonderlands', file=df)
    print('', file=df)
    for event in sorted(potential_strings):
        print(event, file=df)

