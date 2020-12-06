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
    # naive version for files only
    tree_entries = []
    for entry in index:
        mode = str(oct(entry.mode))[2:]
        tree_entry = f"{mode} {entry.name}\0".encode()
        tree_entry += entry.sha1
        tree_entries.append(tree_entry)

    data = "".encode()
    for tree_entry in tree_entries:
        data += tree_entry
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
