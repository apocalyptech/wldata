Wonderlands Data Processing
===========================

A few utilities I use to extract Wonderlands data and massage it into a state
that's most useful for data inspection.  I Run Wonderlands on Linux using
Wine/Proton, so all of these assume Linux as well, so they're probably
not especially useful to most Windows users, alas.

These utilities were all taken from my [bl3data repository](https://github.com/apocalyptech/bl3data)
and modified slightly for use in Wonderlands instead.  The changes required
range from minor to nonexistent, but it didn't quite seem worth trying to
combine the two into a single set.  Note that as of writing, I'm not totally
sure I've got the pakfiles sorted properly, since I didn't buy the game until
it was out on Steam, and there appear to be some differences in how the
pakfiles are packed between EGS and Steam.

- `link_paks.py`: I like to keep WL's pakfiles sorted into dirs which
  correspond to the patches in which they were released.  Pass it a list of
  directories in the current dir which start with `pak-`.  Each `pak-*` dir
  should have a `filelist.txt` in it, which is just a list of the pakfiles
  released in that patch.  This util will update symlinks based on a
  `-s`/`--store` argument (the only valid value is currently `steam`).
  Optionally, it'll also update our checksum files if it's passed
  `-c`/`--checksum`.  (It'll just append to the file.)

  - `checksums-sha256sum-steam.txt`: A list of sha256sum checksums for all
    the pakfiles in WL, from Steam.  As of the Steam release, these
    often differ between platforms, and the list of pakfiles in Steam is
    apparently different than EGS.

- `unpack_wl.py`: Written in conjunction with [apple1417](https://github.com/apple1417/).
  Used to call `UnrealPak.exe` (optionally via Wine, on Linux) to
  uncompress a bunch of PAK files and arrange them into a file structure
  which matches their in-game object names.  Will attempt to autodetect
  your WL install root, but you can also specify pakfiles/directories
  to unpack manually.  Requires an encryption key to unpack WL PAK files,
  which happens to be identical to the key used for Borderlands 3;
  you should be able to find that with a quick internet search for
  `borderlands 3 pakfile aes key`.

- `find_dup_packs.py`: Little utility to see if duplicate PAK files
  exist in any dirs.  Just some sanity checks for myself.

- `paksort.py`: Sorts PAK files passed on STDIN "intelligently," rather
  than just alphanumerically (which would otherwise put `pakchunk21`
  inbetween `pakchunk2` and `pakchunk3`, for instance).  Handles the
  patch filename conventions as well, so patches will show up after
  the files they patch.  Basically this can be used to define an order
  of unpacking.

- `check_object_case.py`: There are some cases where an object filename/path
  unpacks to a name which doesn't use the same case as the object name,
  which can be annoying when on systems with case-sensitive filesystems.
  This utility loops through an extract dir and attempts to find any case
  mismatches in the data, and reports them to stdout.  Those fixes should
  then be ported back into `unpack_wl.py` in the `hardcoded_path_fixes` var.
  Used when unpacking a fresh set of WL data, basically.  Note that this
  script is set to use [PyPy3](https://www.pypy.org/) rather than CPython,
  for speed, though you can of course run it under vanilla CPython instead,
  if you like.

Processing New Data
-------------------

These are my notes of what I do when a new patch is released.  First,
to prep/extract the data:

1. Create a new `pak-YYYY-MM-DD-note` dir, with a `filelist.txt` inside
   which lists the new/update pakfiles
2. Use `link_paks.py` to symlink the pakfiles into the dir, for the given
   store, and generate updated checksums.  Repeat this for both stores,
   if you want both sets of checksums.
3. Unpack the new `pak-*` dir using `unpack_bl3.py`.  This will leave
   an `extracted_new` dir alongside the main `extracted` dir, with the
   new data.

If you don't care about my `pak-*` directory organization, you can just
lump all the paks in a single dir and `unpack_bl3.py` that dir.

License
-------

All code in this project is is licensed under the
[New/Modified (3-Clause) BSD License](https://opensource.org/licenses/BSD-3-Clause).
A copy can be found in [COPYING.txt](COPYING.txt).

