#!/usr/bin/env python3

# This is a Python reimplementation of "metafile" format used in old EPSITEC games
# The syntax is designed to be similar to what the "tar" command uses

import argparse
import binascii
import struct
import itertools
import os.path

# Keys used by games:
# Colobot: full, demo
# Ceebot-A: TODO check
# Ceebot-3: TODO check
# Ceebot-Teen: TODO check
# Ceebot-4 PERSO: full, demo (?TODO check)
# Ceebot-4 SCHOOL: TODO check
# BuzzingCars: full, bcdemo, bcspecialedition
# Blupimania2: full, bcdemo

enckeys = {
    'full': bytearray([
        0x85, 0x91, 0x73, 0xcf, 0xa2, 0xbb, 0xf4, 0x77,
        0x58, 0x39, 0x37, 0xfd, 0x2a, 0xcc, 0x5f, 0x55,
        0x96, 0x90, 0x07, 0xcd, 0x11, 0x88, 0x21
    ]),
    'demo': bytearray([
        0x85, 0x91, 0x77, 0xcf, 0xa3, 0xbb, 0xf4, 0x77,
        0x58, 0x39, 0x37, 0xfd, 0x2a, 0xcc, 0x7f, 0x55,
        0x96, 0x80, 0x07, 0xcd, 0x11, 0x88, 0x21, 0x44,
        0x17, 0xee, 0xf0
    ]),
    'school': bytearray([
        0x72, 0x91, 0x37, 0xdf, 0xa1, 0xcc, 0xf5, 0x67,
        0x53, 0x40, 0xd3, 0xed, 0x3a, 0xbb, 0x5e, 0x43,
        0x67, 0x9a, 0x0c, 0xed, 0x33, 0x77, 0x2f, 0xf2,
        0xe3, 0x42, 0x11, 0x5e, 0xc2
    ]),
    'schooldemo': bytearray([
        0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76,
        0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76,
        0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76,
        0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76,
        0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76,
        0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5
    ]),
    'bcdemo': bytearray([
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5,
        0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83,
        0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83,
        0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83,
        0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83,
        0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83,
        0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83, 0x83,
    ]),
    'bcspecialedition': bytearray([
        0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36,
        0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36,
        0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36,
        0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36,
        0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36,
        0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36,
        0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36,
        0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36,
        0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36,
        0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36, 0x36,
        0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5,
        0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5,
        0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5,
        0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5,
        0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5, 0xC5
    ]),
    'none': None
}

# TODO: Implement Blupi cryptfile support

class Metafile:
    def __init__(self, filename, mode, enckey=None):
        self.filename = filename
        self.mode = mode
        self.enckey = enckey

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def read_encrypted_bytes(self, bytecount):
        pos = self.file.tell()
        bytes = self.file.read(bytecount)
        if self.enckey:
            return bytearray([c^k for c,k in zip(bytes, itertools.islice(itertools.cycle(self.enckey), pos % len(self.enckey), None))])
        else:
            return bytearray(bytes)

    class FileDescriptor:
        def __init__(self, name, start, len):
            self.name = name
            self.start = start
            self.len = len

        def __str__(self):
            return "[File '{}', length {}, starts at {}]".format(self.name, self.len, self.start)

    def file_list(self):
        self.file.seek(0)
        total_files, = struct.unpack("<I", self.file.read(4))
        #print("Total file count: {}".format(total_files))
        HEADER_FORMAT = "<14sxxII"
        HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
        for i in range(total_files):
            self.file.seek(4+i*HEADER_SIZE)
            fname, fstart, flen = struct.unpack(HEADER_FORMAT, self.read_encrypted_bytes(HEADER_SIZE))
            yield self.FileDescriptor(fname.decode('ascii').rstrip('\x00'), fstart, flen)

    def read_file(self, filedesc):
        self.file.seek(filedesc.start)
        return self.read_encrypted_bytes(filedesc.len)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pack or unpack legacy EPSITEC metafile format')
    subparsers = parser.add_subparsers(help='Action', dest='action')
    subparsers.required = True
    #parser_c = subparsers.add_parser('c', help='Create') #TODO
    parser_x = subparsers.add_parser('x', help='eXtract')
    parser_t = subparsers.add_parser('t', help='lisT')
    parser.add_argument('file', help='File to work on')
    parser.add_argument('--enckey', help='Select game encryption key to use. Use one of: {} or an arbitrary hex string'.format(', '.join(enckeys.keys())), required=True)
    parser.add_argument('--destination', help='Change destination directory for extracted files (default: current directory)', default='.')
    parser.add_argument('--verbose', dest='verbose', help='Print file names while extracting', action='store_true')
    args = parser.parse_args()

    enckey = None
    if args.enckey in enckeys:
        enckey = enckeys[args.enckey]
    else:
        enckey = bytearray(binascii.unhexlify(args.enckey))

    if args.action == 't':
        with Metafile(args.file, 'rb', enckey) as metafile:
            print("{:<14}|{:<15}".format("Filename", "Size"))
            print("=" * 30)
            for file in metafile.file_list():
                print("{:<14}|{} B".format(file.name, file.len))
    elif args.action == 'x':
        with Metafile(args.file, 'rb', enckey) as metafile:
            for file in metafile.file_list():
                if args.verbose:
                    print(file.name)
                with open(os.path.join(args.destination, file.name), 'wb') as file2:
                    file2.write(metafile.read_file(file))