# Copyright 2012 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

import os
import types
import imp
import traceback

_overrides = []
_active_module = []


def load(namespace, module):
    global _active_module, _overrides

    _active_module.append(module)
    _overrides.append({})
    try:
        name = __package__ + "." + namespace
        override_module = __import__(name, fromlist=[""])
    except ImportError:
        exc = traceback.format_exc()
        try:
            paths = [os.path.dirname(__file__)]
            fp, pn, desc = imp.find_module(namespace, paths)
        except ImportError:
            pass
        else:
            if fp:
                fp.close()
            print exc
            raise ImportError("Failed to load overrides for %r" % namespace)
    else:
        # inject a module copy into the override module that
        # has the original classes for all overriden ones
        # so the classes can access the bases at runtime

        # XXX: I guess we need a proxy module here....
        # I'm not really sure why this works at all :)
        fake_name = "FakeOverride(%s)" % module.__name__
        orig_cls = type(module)
        orig_dict = dict(orig_cls.__dict__)
        del orig_dict["__init__"]
        new_cls = type(fake_name, orig_cls.__bases__, orig_dict)
        module_copy = new_cls("")
        module_copy.__dict__.update(module.__dict__)

        for name, klass in _overrides[-1].iteritems():
            setattr(module_copy, name, klass)
        vars(override_module)[namespace] = module_copy

    _active_module.pop(-1)
    _overrides.pop(-1)


def duplicate(klass, name):
    global _active_module
    module = _active_module[-1]

    assert not hasattr(module, name)
    setattr(module, name, klass)


def override(klass):
    global _active_module, _overrides
    module = _active_module[-1]

    # FIXME: hack
    if hasattr(klass, "_is_function"):
        def wrap(wrapped):
            setattr(module, klass.__name__, wrapped)
            return wrapped
        return wrap

    old_klass = klass.__mro__[1]
    name = old_klass.__name__
    klass.__name__ = name
    klass.__module__ = old_klass.__module__

    assert getattr(module, name) is old_klass

    setattr(module, name, klass)
    _overrides[-1][name] = old_klass

    return klass
