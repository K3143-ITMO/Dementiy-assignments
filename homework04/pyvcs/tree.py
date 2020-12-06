import os
import pathlib
import stat
import time
import typing as tp
import sys

from pyvcs.index import GitIndexEntry, read_index
from pyvcs.objects import hash_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref


def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:
    """
    Write a tree as a git object and return its' hash
    """
    # State of the function address: returns correct results for files, infinitely recurses for directories
    #list_of_files = something-something no one told me
    list_of_files = [pathlib.Path("animals.txt")] # test
    # basically, we have this in subdirs:
    # .
    #    alphabeta
    #       letters.txt
    #    numbers
    #       digits.txt
    #    quote.txt
    # So the algo should go like this:
    #   alphabeta is a dir -> "040000 alphabeta\0{here we recurse to write_tree}" --------------------------------------------------------|
    #       recursion is here -> letters.txt is a file -> "100644 letters.txt\0{blob_hash}", then we hash it and return to upper level    |
    #|------------------------------------------------------------------------------------------------------------------------------------|
    #|->numbers is a dir -> "040000 numbers\0{here we recurse to write_tree}" ----------------------------------------------------------|
    #       recursion is here -> digits.txt is a file -> "100644 digits.txt\0{blob_hash}", then we hash it and return to upper level    |
    #|----------------------------------------------------------------------------------------------------------------------------------|
    #|->quote.txt is a file -> "100644 quote.txt\0{blob_hash}"
    #
    # End result is kinda like:
    # "040000 alphabeta\0{tree_hash}100644 letters.txt\0{blob_hash}040000 numbers\0{tree_hash}100644 digits.txt\0{blob_hash}100644 quote.txt\0{blob_hash}"
    # Then we hash it and return the result.
    tree_entries = []
    for filename in list_of_files:
        if filename.is_file():
            with filename.open("rb") as f:
                data = f.read()
            mode = str(oct(filename.stat().st_mode))[2:]
            tree_entry = f"{mode} {str(filename)[str(filename).find(os.sep)+1:]}\0".encode()
            tree_entry += bytes.fromhex(hash_object(data, "blob", write=True))
            tree_entries.append(tree_entry)
        else:
            mode = "040000"
            tree_entry = f"{mode} {filename}\0".encode()
            sha = bytes.fromhex(write_tree(gitdir, index, str(filename)))
            tree_entry += sha
            tree_entries.append(tree_entry)

    data = b"".join(tree_entries)
    return hash_object(data, "tree", write=True)

def commit_tree(
    gitdir: pathlib.Path,
    tree: str,
    message: str,
    parent: tp.Optional[str] = None,
    author: tp.Optional[str] = None,
) -> str:
    # PUT YOUR CODE HERE
    ...
