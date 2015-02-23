from packaging.version import Version, parse

ALL = '0.0'
LATEST = '1000000.0'

class UnboundException(Exception):
    pass

def _convert(version):
    if version is None:
        return None
    if not isinstance(version, Version):
        return parse(version)
    return version

class VersionedBase(object):
    def __init__(self, version=None):
        self._version = version

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

class VersionedValue(VersionedBase):
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
    def __init__(self, key, list_or_dict=None, default_version=None):
        super(VersionedValue, self).__init__(default_version)
        self._key = key
        if isinstance(list_or_dict, dict):
            self._construct_from_dict(list_or_dict)
        else:
            self._construct_from_list(list_or_dict)

    def _construct_from_list(self, values):
        self._construct_from_dict({ALL:values})
        self.bind_to_version(ALL)

    def _construct_from_dict(self, values):
        self._values = dict((_convert(k), v) for k, v in values.items())

    def get_values(self):
        if not self.is_bound():
            raise UnboundException('Versioned value {0} is not bound'.format(self._key))
        return self._get_values(raise_exc=True)

    def _get_values(self, raise_exc=False):
        for v in reversed(sorted(self._values.keys())):
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
        return VersionedValue(self._key, self._values, default_version=self._version)

    def __eq__(self, o):
        if isinstance(o, VersionedValue):
            if self.is_bound() and o.is_bound():
                return self._get_values() == o._get_values()
        elif self.is_bound():
            return o in self._get_values()

        return False

    def __ne__(self, o):
        return not self == o
    
    def __getitem__(self, version):
        return self.as_version(version)
    
    def __repr__(self):
        return "{{{0}:{1}}}".format(self._key, self._values)

class VersionedGroup(VersionedBase):
    """
    Create a value group, an emun of versioned values
    
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
    def __init__(self, *values, **kwargs):
        default_version = kwargs.get('default_version', None)
        super(VersionedGroup, self).__init__(default_version)
        self._values = dict((value._key, value.as_version(default_version)) for value in values)

    def __getattribute__(self, key):
        try:
            return super(VersionedGroup, self).__getattribute__(key)
        except AttributeError:
            return self._values[key]

    def __getitem__(self, key):
        return self._values[key]

    def bind_to_version(self, version):
        super(VersionedGroup, self).bind_to_version(version)
        for value in self._values.values():
            value.bind_to_version(version)
            
    def _copy(self):
        return VersionedGroup(*self._values.values(), default_version=self._version)

    def find_value(self, value):
        if not self.is_bound():
            raise UnboundException("Can't lookup value for unbound versioned dict")
        for v in self._values.values():
            if v == value:
                return v
        raise UnboundException('Could not find matching value for {0}'.format(value))

    def __repr__(self):
        return self._values.values().__repr__()
