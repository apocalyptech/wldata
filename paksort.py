#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

# Wonderlands Data Processing Scripts
# Copyright (C) 2019-2022 CJ Kucera
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

import re
import sys

pak_re = re.compile(r'^pakchunk(\d+)(optional)?-WindowsNoEditor(_(\d+)_P)?\.pak$')

class PakFile(object):

    def __init__(self, filename):
        self.filename = filename
        match = pak_re.match(self.filename)
        if match:
            self.paknum = int(match.group(1))
            if match.group(2):
                self.paknum += 0.5
            if match.group(3):
                self.patchnum = int(match.group(4))+1
            else:
                self.patchnum = 0
        else:
            raise Exception('Unknown pak file: {}'.format(filename))
        #print('{}: {}, {}'.format(self.filename, self.paknum, self.patchnum))

        # This order_num value is only really being used by my pakfile lookup
        # web thing, though we should maybe just start using it in __lt__ too...
        self.order_num = self.paknum*10000 + self.patchnum

    def __lt__(self, other):
        return (self.paknum, self.patchnum) < (other.paknum, other.patchnum)

    def __repr__(self):
        return self.filename

if __name__ == '__main__':
    files = []
    for line in sys.stdin.readlines():
        files.append(PakFile(line.strip()))

    for filename in sorted(files):
        print(filename)
