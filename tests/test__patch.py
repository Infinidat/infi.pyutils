import os
from infi.pyutils.patch import patch
from .test_utils import TestCase

def listdir_patch(path):
    return [path]

TEST_PATH = "__infi_test"

class EnumTestCase(TestCase):
    def test__patch_context(self):
        with patch(os, "listdir", listdir_patch):
            result = os.listdir(TEST_PATH)
            self.assertEqual(result, [TEST_PATH])
        self.assertNotEqual(os.listdir('.'), [TEST_PATH])

