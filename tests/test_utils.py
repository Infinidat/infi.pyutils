import platform
if platform.python_version() < '2.7':
    from unittest2 import TestCase
else:
    from unittest import TestCase
