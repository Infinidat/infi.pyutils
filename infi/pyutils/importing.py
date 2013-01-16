import itertools
import logging
import os
import sys
import types

class NoInitFileFound(Exception):
    pass

_logger = logging.getLogger("infi.pyutils.importing")

def import_file(filename):
    module_name = _setup_module_name_for_import(filename)
    returned = sys.modules.get(module_name)
    if returned is None:
        if os.path.isdir(filename):
            filename = os.path.join(filename, "__init__.py")
        returned = __import__(module_name, fromlist=[""])
        sys.modules[module_name] = returned
        assert module_name in sys.modules
    return returned

_package_name_generator = ('AUTOPKG_{0}'.format(x) for x in itertools.count())

def _generate_package_name(dirname):
    for suggested in _package_name_generator:
        if not _package_name_exists(suggested):
            return suggested

def _package_name_exists(pkg_name):
    return pkg_name in sys.modules

def _setup_module_name_for_import(filename):
    returned = _get_existing_module_name(filename)
    if returned is None:
        returned = _create_new_module_name(filename)
    return returned

def _get_existing_module_name(filename):
    return None

_cached_package_names = {}

def _create_new_module_name(filename):
    _logger.debug("Creating new package for %s", filename)
    nonpackage_dir, remainder = _split_nonpackage_dir(filename)
    _logger.debug("After split: %s, %s", nonpackage_dir, remainder)
    package_name = _cached_package_names.get(nonpackage_dir, None)
    if package_name is None:
        package_name = _generate_package_name(nonpackage_dir)
        _logger.debug("Package name for %s is %s", nonpackage_dir, package_name)
        sys.modules[package_name] = _ensure_package_module(package_name, nonpackage_dir)
        _cached_package_names[nonpackage_dir] = package_name
    _ensure_all_packages_imported(nonpackage_dir, package_name, remainder)
    return '{0}.{1}'.format(package_name, remainder)

def _ensure_all_packages_imported(nonpackage_dir, package_name, remainder):
    path = nonpackage_dir
    for x in remainder.split(".")[:-1]:
        package_name += "."
        package_name += x
        path = os.path.join(path, x)
        _ensure_package_module(package_name, path)

def _split_nonpackage_dir(path):
    if not os.path.isdir(path):
        nonpackage_dir, module = os.path.split(os.path.normpath(os.path.abspath(path)))
        module = _make_module_name(module).split(".")
    else:
        nonpackage_dir = path
        module = []
    while os.path.isfile(os.path.join(nonpackage_dir, "__init__.py")):
        if '.' in os.path.split(nonpackage_dir)[-1]:
            # we cannot import from such packages, stop traversing upwards...
            break
        nonpackage_dir, current_component = os.path.split(nonpackage_dir)
        module.insert(0, current_component)
        _logger.debug("Now at %s, %s", nonpackage_dir, module)
    if not module:
        raise NoInitFileFound("Could not find __init__.py file in {0}".format(path))
    return nonpackage_dir, ".".join(module)

def _make_module_name(filename):
    assert filename.endswith('.py') or filename.endswith('.pyc')
    return filename.rsplit(".", 1)[0].replace(os.path.sep, ".")

def _ensure_package_module(name, path):
    returned = sys.modules.get(name)
    if returned is None:
        returned = types.ModuleType(name)
        returned.__path__ = [name]
        returned.__package__ = name
        returned.__file__ = path
        sys.modules[name] = returned
    return returned
