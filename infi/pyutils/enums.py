from packaging.version import Version, parse
from .python_compat import OrderedDict, itervalues

ALL = '0.0'

class UnboundException(AttributeError):
    pass

def _convert(version):
    if version is None:
        return None
    if not isinstance(version, Version):
        return parse(version)
    return version

class VersionedBase(object):
    def __init__(self, version=ALL):
        self._version = _convert(version)

    def as_version(self, version):
        bound = self._copy()
        bound.bind_to_version(version)
        return bound

    def bind_to_version(self, version):
        self._version = _convert(version)

    def is_bound(self):
        return self._version is not None

    def get_bound_version(self):
        return str(self._version) if self._version is not None else None

    def __reduce__(self, *args, **kwargs):
        return (self.__class__, (str(self._version),))


class Value(VersionedBase):
    """
    Create a value list, or a versioned value list. To specify versions, use a dict, otherwise, use a list of values.
    
    Example:
    
    >>> avg = VersionedValue('avg',['avg','Average','AVG'])
    >>> avg == 'avg'
    True
    >>> avg == 'AVG'
    True
    >>> avg == 'AVERAGE'
    False
    
    Versioned example:
    
    >>> avg = VersionedValue('avg',{'1.0':['avg','AVG'],'2.0':['Average','AVERAGE']})
    >>> avg.as_version('1.0') == 'avg'
    True
    >>> avg.as_version('2.0') == 'avg'
    False
    >>> avg.as_version('2.0') == 'Average'
    True    
    
    """
    def __init__(self, key, list_or_dict=None, default_version=ALL, **kwargs):
        super(Value, self).__init__(default_version)
        if isinstance(key, Value):
            key = str(key)
        self._key = str(key)
        if list_or_dict is None:
            list_or_dict = []
        if isinstance(list_or_dict, dict):
            self._construct_from_dict(list_or_dict)
        else:
            if 'aliases' in kwargs:
                # For backwards compatibility with old non versioned enums
                list_or_dict = kwargs.get('aliases')
            self._construct_from_list(list_or_dict)

    def _construct_from_list(self, values):
        converted_values = [self._key]
        for value in values:
            if isinstance(value, Value):
                converted_values.extend(value.get_values())
            else:
                converted_values.append(value)
        self._construct_from_dict({ALL:converted_values})
        self.bind_to_version(ALL)

    def _construct_from_dict(self, values):
        self._values = OrderedDict((_convert(k), values[k]) for k in reversed(sorted(values.keys())))

    def get_name(self):
        return self._key

    def get_values(self):
        if not self.is_bound():
            raise UnboundException('Versioned value {0} is not bound'.format(self._key))
        return self._get_values(raise_exc=True)

    def _get_values(self, raise_exc=False):
        for v in self._values.keys():
            if self._version >= v:
                return self._values[v]
        if raise_exc:
            raise UnboundException('No values of {0} could be found for version {1}'.format(self._key, self._version))
        return []

    def get_value(self):
        values = self.get_values()
        if values:
            return values[0]
        raise UnboundException('No value of {0} could be found for version {1}'.format(self._key, self._version))

    def _copy(self):
        return Value(self._key, self._values, default_version=self._version)

    def __hash__(self, *args, **kwargs):
        return self._key.__hash__()

    def __eq__(self, o):
        compare_values = [str(v).lower() for v in self._get_values()]
        if isinstance(o, Value):
            other_values = [str(v).lower() for v in o._get_values()]
        else:
            other_values = [str(o).lower()]
        return compare_values == other_values or any(v in compare_values for v in other_values)

    def __ne__(self, o):
        return not self == o
    
    def __getitem__(self, version):
        return self.as_version(version)
    
    def __str__(self):
        return self._key.upper()

    def __repr__(self):
        return self._key.upper()

    def __reduce__(self, *args, **kwargs):
        return (self.__class__, (self._key, dict((str(k), v) for k, v in self._values.items()), str(self._version)))

class Enum(VersionedBase):
    """
    An Enum class for python.
    
    >>> x = Enum(VersionedValue("True",{'1.0': ["TRUE"],
                                        '2.0': ["True","yes"]}),
                 VersionedValue("False",{'1.0': ["FALSE"],
                                         '2.0': ["False","No"]}))
    >>> x.true
    TRUE
    >>> "TRUE" in x
    True
    >>> x.false
    FALSE
    >>> x.false == "NOT"
    True
    >>> "NOT" in x
    True
    >>> "FALSE" in x
    True    
    """
    def __init__(self, *values, **kwargs):
        default_version = kwargs.get('default_version', ALL)
        super(Enum, self).__init__(default_version)
        self._values = OrderedDict()
        for value in values:
            if not isinstance(value, Value):
                value = Value(value)
            self._values[str(value)] = value.as_version(default_version)

    def bind_to_version(self, version):
        super(Enum, self).bind_to_version(version)
        for value in itervalues(self._values):
            value.bind_to_version(version)
            
    def _copy(self):
        return Enum(*itervalues(self._values), default_version=self._version)

    def get(self, value):
        if not self.is_bound():
            raise UnboundException("Can't lookup value for unbound versioned dict")
        for v in itervalues(self._values):
            if v == value:
                return v
        raise UnboundException('Could not find matching value for {0}'.format(value))

    def __iter__(self):
        return itervalues(self._values)

    def __getattribute__(self, key):
        if key.startswith('_'):
            return super(Enum, self).__getattribute__(key)
        try:
            return self[key]
        except KeyError:
            return super(Enum, self).__getattribute__(key)

    def __getitem__(self, key):
        if isinstance(key, Value):
            key = str(key)
        return self._values[key.upper()]

    def __repr__(self):
        return [v for v in itervalues(self._values)].__repr__()

    def __reduce__(self, *args, **kwargs):
        return (self.__class__, tuple(itervalues(self._values)), {'default_version':str(self._version)})
    
    def __setstate__(self, state):
        if '_values' in state:
            self._values = state['values']
        if 'default_version' in state:
            self.bind_to_version(state['default_version'])
        
    def __eq__(self, other):
        if type(self) != type(other):
            return NotImplemented
        return self._version == other._version and self._values == other._values
