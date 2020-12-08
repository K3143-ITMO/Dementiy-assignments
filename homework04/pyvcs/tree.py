"""
Operations on Git tree objects
"""
import os
import pathlib
import stat
import sys
import time
import typing as tp

from pyvcs.index import GitIndexEntry, read_index
from pyvcs.objects import hash_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref


def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:
    """
    Write a tree as a git object and return its' hash
    """
    tree_entries = []
    for entry in index:
        if dirname:  # if we got in here from a recursive call
            prefix, name = os.path.split(
                dirname
            )  # yield a path before the name and the name itself
            # i.e, "/foo/bar/baz" -> prefix=="/foo/bar", name=="baz"
        else:  # not from a recursive call, start at the entry name
            prefix, name = os.path.split(entry.name)
        if prefix:  # if we have is in a directory
            start, _ = os.path.split(prefix)  # start splitting off chunks of the path
            while start.find(os.sep) != -1:  # we can't stop until we get the new full path
                # (from dirname to the entry.name file)
                start, remainder = os.path.split(start)
                name = remainder + name  # add to the path
            mode = "40000"  # mode magic
            tree_entry = f"{mode} {prefix}\0".encode()
            tree_entry += bytes.fromhex(
                write_tree(gitdir, index, name)
            )  # recursively call write_tree to add the underlying directory as a tree
            tree_entries.append(tree_entry)  # adds the directory that exists in the root
        else:  # we have a file
            if (
                dirname and entry.name.find(dirname) == -1
            ):  # if dirname exists, but does not point to the current file
                continue  # skip the file when creating subtree
            with open(entry.name, "rb") as content:
                data = content.read()
            mode = str(oct(entry.mode))[2:]
            tree_entry = f"{mode} {name}\0".encode()
            tree_entry += bytes.fromhex(hash_object(data, "blob", write=True))
            tree_entries.append(tree_entry)

    tree_binary = b"".join(tree_entries)
    return hash_object(tree_binary, "tree", write=True)


def commit_tree(
    gitdir: pathlib.Path,
    tree: str,
    message: str,
    parent: tp.Optional[str] = None,
    author: tp.Optional[str] = None,
) -> str:
    """
    Commit a tree
    """
    # PUT YOUR CODE HERE
    ...
