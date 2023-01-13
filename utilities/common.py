# -*- coding: utf-8 -*-
# description     : Common utilities
# author          : Shixi CHEN
# ==============================================================================
from logging import debug, info, warning, error, critical
import yaml
import os
import errno
import collections
# import pandas as pd

def loadYaml(yamlFile, Loader=yaml.FullLoader):
    """Load a yaml file, trim comment lines and catch any exceptions.

    Args:
        yamlFile (str): Path to the file to open.
        loader: yaml utilities that manipulate the input stream

    Returns:
        result (dict): A dict that is a direct translation of the YAML file
    """
    if yamlFile == None:
        return None

    assert (os.path.isfile(yamlFile))
    result = None
    try:
        with open(yamlFile, "r") as f:
            result = yaml.load(f, Loader=Loader)
    except IOError as err:
        error("YAML file " + yamlFile + " was not found!")
        raise err
    return result

def loadYamlAsString(yamlFile):
    """Load a yaml file, but all values are treated as string

    Args:
        yamlFile (str, optional): Path to the file to open.

    Returns:
        result (dict): A dict that is a direct translation of the YAML file
    """
    return loadYaml(yamlFile, Loader=yaml.BaseLoader)
    

def mkdirP(path):
    """ Make a directory without raising exceptions
    """
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def safeOpen(path, mode="w"):
    """ Open "path" for writing, creating any parent directories as needed.
    """
    mkdirP(os.path.dirname(path))
    return open(path, mode)

def flattenDict(d, parent_key="", sep="."):
    """Flatten {"a": 1, "c": {"a": 2, "b": {"x": 3, "y": 4}}, "d": [6, 7, 8]}
       to      {"a": 1, "c.a": 2, "c.b.x": 3, "c.b.y": 4, "d": [6, 7, 8]}
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flattenDict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def sortDict(d, byKey=True, reverse=False):
    if byKey:
        return sorted(d.items(), key=lambda x: x[0], reverse=reverse)
    else:
        return sorted(d.items(), key=lambda x: x[1], reverse=reverse)

def dataFrameToCsv(dataFrame, outPath: str):
    dataFrame.to_csv(outPath, sep="\t", encoding="utf-8", index=False)

def nestedDictIterator(dictObj):
    """ This function accepts a nested dictionary as argument
        and iterate over all values of nested dictionaries
    """
    # Iterate over all key-value pairs of dict argument
    for key, value in dictObj.items():
        # Check if value is of dict type
        if isinstance(value, dict):
            # If value is dict then iterate over all its values
            for pair in  nestedDictIterator(value):
                yield (key, *pair)
        else:
            # If value is not dict type then yield the value
            yield (key, value)