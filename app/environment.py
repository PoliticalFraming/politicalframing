"""
Add the boilerplate's directories to Python's site-packages path.
source: https://github.com/bueda/tornado-boilerplate/blob/master/environment.py
"""

import os
import site
import sys

ROOT = os.path.dirname(os.path.realpath(__file__))
path = lambda *a: os.path.join(ROOT, *a)
prev_sys_path = list(sys.path)

if os.path.exists(path('../lib')):
    for directory in os.listdir(path('../lib')):
        full_path = path('../lib/%s' % directory)
        if os.path.isdir(full_path):
            site.addsitedir(full_path)

# Move the new items to the front of sys.path. (via virtualenv)
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path