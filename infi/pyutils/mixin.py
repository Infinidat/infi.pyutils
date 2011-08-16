"""
===============
Mixin utilities
===============

The concept here is to add functionality by inheritence in *runtime* (vs. when coding).

For example, let's say you have a ``HttpRequest`` object. Now let's say that you have some additional functionality
such as authentication/authorization that exists only if some HTTP headers exist in *this* request. One way to do it is
to create an ``UserAuthHttpRequest`` class that extends the ``HttpRequest`` with the new functionality. But here's the
catch - you only know that this functionality can be added *after* you created the object. Even if you could deduce it
beforehand, there are still scenarios where there are several different functionality "modules" you may want to add and
writing the entire matrix beforehand is pretty annoying, not to mention that testing all these combinations is
exhausting.

Enter mixins. Mixins are classes that add functionality to an existing class. A mixin relies on the existance of methods
or attributes on the object, and may use them to add more functionality. So in our case, we'll want to have a
``UserAuth`` mixin that assumes that there's *self.get_header(name)* method::

class HttpRequest(object):
    def get_header(self, name):
        ...
class UserAuth(object):
    def is_authenticated(self):
        auth_header = self.get_header("Authorization")
        ...

Now, to add the mixin to the object we'll do::

request = HttpRequest(...)

# Find out that there's a need for authentication
...

install_mixin(request, HttpRequest, UserAuth)
"""
from .lazy import cached_function

__all__ = [ "install_mixin", "install_mixin_if" ]

def install_mixin_if(obj, klass, mixin, condition):
    """
    Same as install_mixin, but installs the mixin only if *condition* evaluates to truth.
    """
    if not condition:
        return
    install_mixin(obj, klass, mixin)

def install_mixin(obj, klass, mixin):
    obj.__class__ = _replace_class(type(obj), klass, mixin)

@cached_function
def _replace_class(cls, cls_to_add_mixin, mixin):
    if not issubclass(cls, cls_to_add_mixin):
        # No need to search, cls_to_add_mixin isn't in this tree.
        result_cls = cls
    elif getattr(cls, '__mixin_shadow__', None) == cls_to_add_mixin:
        if mixin in cls.__mixins__:
            # Class is already a shadow for cls_to_add_mixin and with the mixin we want.
            result_cls = cls
        else:
            # Class is already a shadow for cls_to_add_mixin, so we'll create a new shadow class with the added mixin.
            mixins = [ mixin ] + cls.__mixins__
            bases = [ mixin ] + list(cls.__bases__)
            result_cls = type('%s[shadow for mixins %s]' % (cls.__name__, ", ". join([ m.__name__ for m in mixins ])),
                              tuple(bases), dict(__mixins__=mixins, __mixin_shadow__=cls_to_add_mixin))
            result_cls.__module__ = cls.__module__
    elif cls == cls_to_add_mixin:
        # This is the class we want to add the mixin to, so we'll create a new subclass of (mixin, cls_to_add_mixin)
        result_cls = type('%s[shadow for mixins %s]' % (cls.__name__, mixin.__name__), (mixin, cls),
                          dict(__mixins__=[ mixin ], __mixin_shadow__=cls_to_add_mixin))
        result_cls.__module__ = cls.__module__
    else:
        # Nothing matched, so we'll traverse the base classes and see.
        new_bases = [ _replace_class(base_cls, cls_to_add_mixin, mixin) for base_cls in cls.__bases__ ]
        if new_bases != cls.__bases__:
            result_cls = type('%s[implicit mixin %s]' % (cls.__name__, mixin.__name__),
                              tuple([ cls ] + new_bases),
                              dict(__implicit_mixins__=[ mixin ], __mixins__=[], __mixin_shadow__=cls))
            result_cls.__module__ = cls.__module__
        else:
            result_cls = cls

    return result_cls
