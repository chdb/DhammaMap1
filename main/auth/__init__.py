# coding: utf-8
# pylint: disable=wildcard-import
"""
Provides logic for authenticating users
"""
import config

from .auth import *

import importlib

apList = config.CONFIG_DB.authProviders 
for i in apList:
    importlib.import_module('auth.'+i.name)
   # importlib.import_module(i.name)
    
# from .bitbucket import *
# from .dropbox import *
# from .facebook import *
# from .github import *
# from .google import *
# from .instagram import *
# from .linkedin import *
# from .microsoft import *
# from .twitter import *
# from .vk import *
# from .yahoo import *
