from types import MethodType
import copy
import inspect
import itertools
import platform
from .exceptions import (
    SignatureException,
    InvalidKeywordArgument,
    UnknownArguments,
    MissingArguments,
    )
from numbers import Number

_IS_PY3 = platform.python_version() >= '3'
if _IS_PY3:
    iteritems = dict.items
    izip = zip
    basestring = str
else:
    izip = itertools.izip
    iteritems = dict.iteritems

_NO_DEFAULT = object()

class Argument(object):
    def __init__(self, name, default=_NO_DEFAULT):
        super(Argument, self).__init__()
        self.name = name
        self.default = default
    def has_default(self):
        return self.default is not _NO_DEFAULT

class FunctionSignature(object):
    def __init__(self, func):
        super(FunctionSignature, self).__init__()
        self.func = func
        self.func_name = func.__name__
        self._build_arguments()
    def is_bound_method(self):
        return is_bound_method(self.func)
    def is_class_method(self):
        return is_class_method(self.func)
    def _iter_args_and_defaults(self, args, defaults):
        defaults = [] if defaults is None else defaults
        filled_defaults = itertools.chain(itertools.repeat(_NO_DEFAULT, len(args) - len(defaults)), defaults)
        return izip(args, filled_defaults)

    def _build_arguments(self):
        self._args = []
        try:
            args, varargs_name, kwargs_name, defaults = inspect.getargspec(self.func)
        except TypeError:
            args = []
            varargs_name = 'args'
            kwargs_name = 'kwargs'
            defaults = []
        for arg_name, default in self._iter_args_and_defaults(args, defaults):
            self._args.append(Argument(arg_name, default))
        self._varargs_name = varargs_name
        self._kwargs_name = kwargs_name
    def get_args(self):
        return itertools.islice(self._args, 1 if self.is_bound_method() else 0, None)
    def get_num_args(self):
        returned = len(self._args)
        if self.is_bound_method():
            returned = max(0, returned - 1)
        return returned
    def get_self_arg_name(self):
        if self.is_bound_method() and len(self._args) > 0:
            return self._args[0].name
        return None
    def get_arg_names(self):
        return (arg.name for arg in self.get_args())
    def get_required_arg_names(self):
        return set(arg.name for arg in self.get_args() if not arg.has_default())
    def has_variable_args(self):
        return self._varargs_name is not None
    def has_variable_kwargs(self):
        return self._kwargs_name is not None
    def get_normalized_args(self, args, kwargs):
        returned = {}
        self._update_normalized_positional_args(returned, args)
        self._update_normalized_kwargs(returned, kwargs)
        self._check_missing_arguments(returned)
        self._check_unknown_arguments(returned)
        return returned
    def _update_normalized_positional_args(self, returned, args):
        argument_names = list(self.get_arg_names())
        argument_names.extend(range(len(args) - self.get_num_args()))
        for arg_name, given_arg in zip(argument_names, args):
            returned[arg_name] = given_arg

    def _update_normalized_kwargs(self, returned, kwargs):
        for arg_name, arg in iteritems(kwargs):
            if not isinstance(arg_name, basestring):
                raise InvalidKeywordArgument("Invalid keyword argument %r" % (arg_name,))
            if arg_name in returned:
                raise SignatureException("%s is given more than once to %s" % (arg_name, self.func_name))
            returned[arg_name] = arg

    def _check_missing_arguments(self, args_dict):
        required_arguments = self.get_required_arg_names()
        missing_arguments = required_arguments - set(args_dict)
        if missing_arguments:
            raise MissingArguments("The following arguments were not specified: %s" % ",".join(map(repr, missing_arguments)))
    def _check_unknown_arguments(self, args_dict):
        positional_arg_count = len([arg_name for arg_name in args_dict if isinstance(arg_name, Number)])
        num_args = self.get_num_args()
        if positional_arg_count and not self.has_variable_args():
            raise UnknownArguments("%s receives %s positional arguments (%s specified)" % (self.func_name, num_args, num_args + positional_arg_count))
        unknown = set(arg for arg in args_dict if not isinstance(arg, Number)) - set(self.get_arg_names())
        if unknown and not self.has_variable_kwargs():
            raise UnknownArguments("%s received unknown argument(s): %s" % (self.func_name, ",".join(unknown)))



def is_bound_method(obj):
    return isinstance(obj, MethodType) and _has_self(obj)
def is_function(obj):
    return isinstance(obj, FunctionType) or isinstance(obj, BuiltinFunctionType)
def is_class(obj):
    return isinstance(obj, type) or isinstance(obj, ClassType)
def _has_self(f):
    return _get_self(f) is not None
def _get_self(f):
    if _IS_PY3:
        return f.__self__
    return f.im_self
def is_class_method(obj):
    if not is_bound_method(obj):
        return False
    return is_class(_get_self(obj))
