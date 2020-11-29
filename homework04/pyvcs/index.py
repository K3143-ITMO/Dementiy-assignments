import hashlib
import operator
import os
import pathlib
import struct
import typing as tp
import sys

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        values = (self.ctime_s, self.ctime_n, self.mtime_s, self.mtime_n, self.dev, self.ino, self.mode, self.uid, self.gid, self.size) # ints prepared for straight-forward packing
        bytecast_values = tuple([i.to_bytes(4, "big") for i in values]) # convert to network byte order
        bytecast_str = struct.pack("4s4s4s4s4s4s4s4s4s4s", *bytecast_values) # pack using 10 4bytes objects because FUCK FORMAT STRINGS
        bytecast_str += self.sha1 # simply concatenate
        bytecast_str += self.flags.to_bytes(2, "big") # cast to network order, truncate to 2 and concatenate
        bytecast_str += self.name.encode("ascii") # simply concatenate encoded string
        if not len(bytecast_str) % 4 == 0: # if struct is not aligned to 4 byte-divisible size
            padding_size = 4 - (len(bytecast_str) % 4) # calculate padded size
            # align size - remaining symbols to align
            print(f"padding required, apadding: {padding_size}", file=sys.stderr)
        for i in range(0, padding_size):
            bytecast_str += b"\x00"        
        return bytecast_str

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        # PUT YOUR CODE HERE
        ...


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    # PUT YOUR CODE HERE
    ...


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    # PUT YOUR CODE HERE
    ...


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    # PUT YOUR CODE HERE
    ...


def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    # PUT YOUR CODE HERE
    ...
