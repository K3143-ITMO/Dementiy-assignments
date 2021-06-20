"""
Git index operations
"""
import hashlib
import os
import pathlib
import string
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    """
    An index entry in readable format
    """

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
        """
        Pack into index format
        """
        values = (
            self.ctime_s,
            self.ctime_n,
            self.mtime_s,
            self.mtime_n,
            self.dev,
            self.ino & 0xFFFFFFFF,  # truncate to 4 bytes
            self.mode,
            self.uid,
            self.gid,
            self.size,
            self.sha1,
            self.flags,
        )  # ints prepared for straight-forward packing
        bytecast_str = struct.pack("!LLLLLLLLLL20sH", *values)  # pack
        bytecast_str += self.name.encode("ascii")  # simply concatenate the encoded string
        if not len(bytecast_str) % 8 == 0:  # if struct is not aligned to 8 byte-divisible size
            padding_size = 8 - (len(bytecast_str) % 8)  # calculate padded size
            # align size - remaining symbols to align
            for _ in range(0, padding_size):  # pad the entry
                bytecast_str += b"\x00"
        return bytecast_str

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        """
        Unpack into readable format
        """
        last_byte = data[-1]  # start at something
        while not last_byte:  # check for NUL padding
            data = data[:-1]  # remove it
            last_byte = data[-1]  # update last_byte
        name = ""
        while chr(last_byte) in (
            string.ascii_letters + string.punctuation + string.digits
        ):  # name can't contain non-character bytes
            name += chr(last_byte)  # add the letter to the name
            data = data[:-1]  # remove it from the data stream
            last_byte = data[-1]  # update last_char
        name = name[::-1]  # reverses the name (i. e, "txt.rab" converts to "bar.txt")
        unpacked = struct.unpack("!LLLLLLLLLL20sH", data)
        index_entry = GitIndexEntry(
            unpacked[0],
            unpacked[1],
            unpacked[2],
            unpacked[3],
            unpacked[4],
            unpacked[5],
            unpacked[6],
            unpacked[7],
            unpacked[8],
            unpacked[9],
            unpacked[10],
            unpacked[11],
            name,
        )  # construct the index entry
        return index_entry


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    """
    Get index entries in readable format from index
    """
    index_entries = []
    if not (gitdir / "index").is_file():  # no index detected, return an empty list
        return []
    with open(gitdir / "index", "rb") as index_file:
        data = index_file.read()
    entry_count = struct.unpack("!i", data[8:12])[0]
    data = data[12:]  # truncate byte stream
    for _ in range(entry_count):  # for each entry
        entry = data[:60]  # 60 bytes are 10 4 byte ints + 20 byte sha
        flags = data[60:62]  # 2-byte flags
        data = data[62:]  # truncate byte stream
        entry += flags
        num_flags = int.from_bytes(flags, "big")  # cast to int
        # namelen will be equal to flags because every other flag bit is 0
        # (Dementiy magic)
        name = data[:num_flags].decode()
        data = data[num_flags:]
        # not implementing getting name if namelen > 0xFFF
        entry += name.encode()
        while True:  # just don't touch this, plz
            if len(data) == 0:
                break  # no entries left, abort
            byte = chr(data[0])
            if byte != "\x00":
                break  # not padding
            entry += byte.encode("ascii")  # add padding
            data = data[1:]  # truncate byte from byte stream

        entry_unpacked = GitIndexEntry.unpack(entry)
        index_entries.append(entry_unpacked)

    return index_entries


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    """
    Write entries to index
    """
    with open(gitdir / "index", "wb") as index_file:
        version = 2  # we only use version 2
        version_bytecast = version.to_bytes(4, "big")
        entries_len_bytecast = len(entries).to_bytes(4, "big")
        index_content = "DIRC".encode()
        index_content += version_bytecast
        index_content += entries_len_bytecast
        for entry in entries:
            index_content += entry.pack()
        # we don't use extensions
        index_sha = hashlib.sha1(index_content).digest()  # in binary
        index_content += index_sha
        index_file.write(index_content)


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    """
    Get indexed files' details
    """
    index_entries = read_index(gitdir)
    if details:
        for entry in index_entries:
            mode = str(oct(entry.mode))[
                2:
            ]  # get mode in decimal, convert to octal, convert to string, strip prefix ("0o")
            sha = entry.sha1.hex()
            stage = (entry.flags >> 12) & 3  # Dementiy bit-field magic
            print(f"{mode} {sha} {stage}\t{entry.name}")
    else:
        for entry in index_entries:
            print(f"{entry.name}")


def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    """
    Update index by adding new files
    """
    index_entries: tp.List[GitIndexEntry] = []
    absolute_paths = [i.absolute() for i in paths]  # get absolute paths
    absolute_paths.sort()  # sort by them
    relative_paths = [
        i.relative_to(os.getcwd()) for i in absolute_paths
    ]  # revert back to relative paths
    relative_paths.reverse()  # reverse the list because sorting discarding length is hard
    for path in relative_paths:  # finally
        with open(path, "rb") as f_name:
            data = f_name.read()  # read data
        obj_hash = bytes.fromhex(hash_object(data, "blob", True))  # write the object
        os_stats = os.stat(path, follow_symlinks=False)  # i hope nobody uses links in repos
        name_len = len(str(path))
        if name_len > 0xFFF:  # bit field magic
            name_len = 0xFFF
        flags = name_len
        # 1 bit assume-valid (will be 0 for now) because Dementiy said so
        # 2 bit 0 because we use version 2,
        # 13 bits name_len (or 0xFFF)
        # So overall flags == name_len
        index_entry = GitIndexEntry(
            int(os_stats.st_ctime),  # apparently this is float
            0,
            int(os_stats.st_mtime),  # apparently this is float
            0,
            os_stats.st_dev,
            os_stats.st_ino,
            os_stats.st_mode,
            os_stats.st_uid,
            os_stats.st_gid,
            os_stats.st_size,
            obj_hash,
            flags,
            str(path),
        )
        if index_entry not in index_entries:  # skip existing entries
            index_entries.insert(0, index_entry)

    if write:
        write_index(gitdir, index_entries)
