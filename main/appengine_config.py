# coding: utf-8
"""
This module inserts third party libraries into Google's python PATHs
In production we import this from lib.zip file, whereas in development
from main/lib folder
"""
import os
import sys

# show the sys path
import logging
logging.info("sys.path: ")
for i in sys.path: logging.info('\t'+i)

if os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine'):
    sys.path.insert(0, 'lib.zip')
else:
    import re

    # The line below does not work!!!(worked in previous version of sdk) - we get "ImportError: cannot import name stubs"
    #   from google.appengine.tools.devappserver2.python import stubs
    #
    # Nor this one, although it's the solution found by google
    #   from google.appengine.tools.devappserver2.python.runtime import stubs
    #
    # But this line does work:
    from google.appengine.tools.devappserver2.python.runtime.stubs import FakeFile
    # This imports  "FakeFile"  instead of "stubs" so below we have replaced  "stubs.FakeFile" with "FakeFile"

    # since lib folder is normally in skip_files in yaml, while developing
    # we want server to include this folder, so we remove it from skip_files
    re_ = FakeFile._skip_files.pattern.replace('|^lib/.*', '')  # pylint: disable=protected-access
    re_ = re.compile(re_)
    FakeFile._skip_files = re_ # pylint: disable=protected-access
    sys.path.insert(0, 'lib')
sys.path.insert(0, 'libx')

# appengine_config.py
#from google.appengine.ext import vendor

# Add any libraries install in the "lib" folder.
#vendor.add('lib')
