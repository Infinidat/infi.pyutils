import itertools
import uuid
import tempfile
import os
import sys
from .test_utils import TestCase
from infi.pyutils import importing

_filename_generator = ("module{0}.py".format(i) for i in itertools.count())

class ImportingTest(TestCase):
    def setUp(self):
        super(ImportingTest, self).setUp()
        self._old_sys_modules = sys.modules.copy()
        self._old_sys_path = sys.path[:]
        self.root = tempfile.mkdtemp()
    def tearDown(self):
        sys.modules = self._old_sys_modules
        sys.path[:] = self._old_sys_path
        super(ImportingTest, self).tearDown()
    def test__import_from_non_package(self):
        self._import_and_verify(self._create_modules([tempfile.mkdtemp()]))
    def test__multiple_imports_from_same_non_package(self):
        filenames_and_expected_values = self._create_modules([self.root, self.root])
        module1, module2 = self._import_and_verify(filenames_and_expected_values)
        self.assertEquals(_PACKAGE_NAME(module1), _PACKAGE_NAME(module2))
        self.assertIsNot(module1, module2)
    def test__importing_sub_package(self):
        subpackage_dir = os.path.join(self.root, "subpackage")
        os.makedirs(subpackage_dir)
        _touch(subpackage_dir, "__init__.py")
        full_filename, expected_value = self._create_module(subpackage_dir, "module.py")
        module = importing.import_file(full_filename)
        self.assertTrue(module.__name__.endswith(".subpackage.module"))
    def test__importing_sub_package_and_subdir(self):
        to_verify = self._create_modules([self.root])
        [module] = self._import_and_verify(to_verify)
        package_name = _PACKAGE_NAME(module)
        to_verify = self._create_modules([os.path.join(self.root, "sub")])
        _touch(self.root, "sub", "__init__.py")
        [sub_module] = self._import_and_verify(to_verify)
        self.assertEquals(_PACKAGE_NAME(module) + ".sub",
                          _PACKAGE_NAME(sub_module))
    def test__importing_different_directories_same_escaping(self):
        dir1 = os.path.join(self.root, "pkg+")
        dir2 = os.path.join(self.root, "pkg-")
        filenames_and_expected_values = self._create_modules([dir1, dir2])
        module1, module2 = self._import_and_verify(filenames_and_expected_values)
        self.assertNotEquals(_PACKAGE_NAME(module1),
                             _PACKAGE_NAME(module2))
    def test__importing_dotted_name(self):
        path_components = ["a", "b.c", "d"]
        path = self.root
        for c in path_components:
            path = os.path.join(path, c)
            os.makedirs(path)
            _touch(path, "__init__.py")
        filename, expected_value = self._create_module(path, "module.py")
        self._import_and_verify([(filename, expected_value)])
    def test__importing_directory_no_init_file(self):
        with self.assertRaises(importing.NoInitFileFound):
            importing.import_file(self.root)
    def test__importing_directory_directly(self):
        self._test__importing_directory(False)
    def test__importing_directory_through_init_py(self):
        self._test__importing_directory(True)
    def _test__importing_directory(self, init_py_directly):
        directory = os.path.join(self.root, "pkg")
        os.makedirs(directory)
        _, expected_value = self._create_module(directory, "__init__.py")
        if init_py_directly:
            module = importing.import_file(os.path.join(directory, "__init__.py"))
        else:
            module = importing.import_file(directory)
        self.assertRaises(module.__name__.endswith(".pkg"))
        self.assertEquals(module.value, expected_value)
    def _create_modules(self, directories):
        returned = []
        for directory in directories:
            if not os.path.isdir(directory):
                os.makedirs(directory)
            returned.append(self._create_module(directory))
        return returned
    def _create_module(self, directory, filename=None):
        id = repr(uuid.uuid1())
        if filename is None:
            filename = next(_filename_generator)
        full_filename = os.path.join(directory, filename)
        with open(full_filename, "w") as f:
            f.write("value = {0!r}".format(id))
        return full_filename, id
    def _import_and_verify(self, filenames_and_expected_values):
        returned = []
        for filename, expected_value in filenames_and_expected_values:
            module = importing.import_file(filename)
            self.assertEquals(module.value, expected_value)
            returned.append(module)
        return returned

def _touch(*p):
    with open(os.path.join(*p), "a"):
        pass

def _PACKAGE_NAME(m):
    return m.__name__.rsplit(".", 1)[0]
