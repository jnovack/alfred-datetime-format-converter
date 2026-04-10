# -*- coding: utf-8 -*-
import itertools
import os
import plistlib
import unicodedata
import sys

from xml.etree.ElementTree import Element, SubElement, tostring

"""
You should run your script via /bin/bash with all escape options ticked.
The command line should be

python yourscript.py "{query}" arg2 arg3 ...
"""
UNESCAPE_CHARACTERS = u""" ;()"""

_MAX_RESULTS_DEFAULT = 9

with open(os.path.join(os.path.dirname(__file__), 'info.plist'), 'rb') as plist_fp:
    preferences = plistlib.load(plist_fp)
bundleid = preferences['bundleid']

class Item(object):
    @classmethod
    def to_text(cls, value):
        try:
            items = value.items()
        except AttributeError:
            return str(value)
        else:
            return {str(k): str(v) for (k, v) in items}

    def __init__(self, attributes, title, subtitle, icon=None):
        self.attributes = attributes
        self.title = title
        self.subtitle = subtitle
        self.icon = icon

    def __str__(self):
        return tostring(self.xml(), encoding='unicode')

    def xml(self):
        item = Element('item', self.to_text(self.attributes))
        for attribute in ('title', 'subtitle', 'icon'):
            value = getattr(self, attribute)
            if value is None:
                continue
            try:
                (value, attributes) = value
            except Exception:
                attributes = {}
            SubElement(item, attribute, self.to_text(attributes)).text = str(value)
        return item

def args(characters=None):
    return tuple(unescape(decode(arg), characters) for arg in sys.argv[1:])

def config():
    return _create('config')

def decode(s):
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    return unicodedata.normalize('NFC', s)

def uid(uid):
    return '-'.join(map(str, (bundleid, uid)))

def unescape(query, characters=None):
    for character in (UNESCAPE_CHARACTERS if (characters is None) else characters):
        query = query.replace('\\%s' % character, character)
    return query

def work(volatile):
    var_name = 'alfred_workflow_cache' if bool(volatile) else 'alfred_workflow_data'
    path = os.getenv(var_name)
    if not path:
        raise RuntimeError('Missing Alfred workflow path env var: %s' % var_name)
    return _create(path)

def write(text):
    if isinstance(text, bytes):
        sys.stdout.buffer.write(text)
        return
    sys.stdout.write(text)

def xml(items, maxresults=_MAX_RESULTS_DEFAULT):
    root = Element('items')
    for item in itertools.islice(items, maxresults):
        root.append(item.xml())
    return tostring(root, encoding='utf-8')

def _create(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    if not os.access(path, os.W_OK):
        raise IOError('No write access: %s' % path)
    return path
