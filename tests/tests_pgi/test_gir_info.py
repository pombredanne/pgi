# Copyright 2012,2014 Christoph Reiter
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

import unittest


class _GIInfoTest(unittest.TestCase):

    gir = None

    def setUp(self):
        self.repo = repo = self.gir.GIRepository.get_default()

        typelib = repo.require(b"Gtk", b"3.0", 0)
        self.assertTrue(typelib)

        typelib = repo.require(b"Gdk", b"3.0", 0)
        self.assertTrue(typelib)

    def _get_gtk(self, name):
        info = self.repo.find_by_name("Gtk", name)
        self.assertTrue(info)
        return info

    def _get_gdk(self, name):
        info = self.repo.find_by_name("Gdk", name)
        self.assertTrue(info)
        return info

    def test_baseinfo(self):
        b = self._get_gtk(b"Button")
        repr(b)
        self.failUnlessEqual(b.name, b"Button")
        self.failUnlessEqual(b.namespace, b"Gtk")
        self.failUnlessEqual(b.is_deprecated, False)
        self.failIf(b.get_container())
        self.failUnlessEqual(b.type.value, self.gir.GIInfoType.OBJECT)
        repr(b.get_typelib())

    def test_typelib(self):
        w = self._get_gtk(b"Window")
        t = w.get_typelib()
        repr(t)
        self.failUnlessEqual(t.namespace, b"Gtk")

    def test_objectinfo(self):
        e = self._get_gtk(b"Expander")
        self.assertTrue(isinstance(e, self.gir.GIObjectInfo))
        repr(e)
        self.failUnlessEqual(e.type_name, b"GtkExpander")
        self.failUnlessEqual(e.type_init, b"gtk_expander_get_type")

        e.get_methods()
        e.get_fields()
        e.get_interfaces()
        e.get_properties()
        e.get_signals()
        e.get_vfuncs()
        e.get_constants()

    def test_enuminfo(self):
        t = self._get_gtk(b"WindowType")
        self.assertTrue(isinstance(t, self.gir.GIEnumInfo))
        repr(t)
        self.failUnlessEqual(t.n_methods, 0)
        self.failUnlessEqual(t.storage_type.value, self.gir.GITypeTag.UINT32)
        self.failUnlessEqual(t.get_value(0).value_, 0)

        t.get_values()
        t.get_methods()

    def test_unioninfo(self):
        e = self._get_gdk(b"Event")
        self.assertTrue(isinstance(e, self.gir.GIUnionInfo))
        repr(e)

        e.get_methods()
        e.get_fields()

    def test_valueinfo(self):
        t = self._get_gtk(b"WindowType")
        self.assertTrue(isinstance(t, self.gir.GIEnumInfo))
        v = t.get_value(0)
        repr(v)

    def test_functioninfo(self):
        e = self._get_gtk(b"Expander")
        self.assertTrue(isinstance(e, self.gir.GIObjectInfo))

        fi = e.get_method(10)
        self.assertTrue(isinstance(fi, self.gir.GIFunctionInfo))
        repr(fi)
        self.failUnlessEqual(fi.symbol, b"gtk_expander_set_expanded")
        self.failUnlessEqual(fi.flags.value,
                             self.gir.GIFunctionInfoFlags.IS_METHOD)

        w = self._get_gtk(b"Window")
        self.assertTrue(isinstance(w, self.gir.GIObjectInfo))
        for fi in w.get_methods():
            repr(fi)

    def test_structinfo(self):
        s = self._get_gtk(b"TargetEntry")
        self.assertTrue(isinstance(s, self.gir.GIStructInfo))
        s.get_fields()
        repr(s)

    def test_fieldinfo(self):
        s = self._get_gtk(b"TargetEntry")
        self.assertTrue(isinstance(s, self.gir.GIStructInfo))
        f = s.get_field(0)
        self.assertTrue(isinstance(f, self.gir.GIFieldInfo))
        repr(f)

    def test_callableinfo(self):
        e = self._get_gtk(b"Expander")
        self.assertTrue(isinstance(e, self.gir.GIObjectInfo))
        fi = e.get_method(9)
        self.assertTrue(isinstance(fi, self.gir.GICallableInfo))
        repr(fi)

    def test_interfaceinfo(self):
        i = self._get_gtk(b"Editable")
        self.assertTrue(isinstance(i, self.gir.GIInterfaceInfo))
        repr(i)

        i.get_methods()
        i.get_properties()
        i.get_signals()
        i.get_constants()
        i.get_prerequisites()
        i.get_vfuncs()

    def test_propertyinfo(self):
        e = self._get_gtk(b"Expander")
        self.assertTrue(e, self.gir.GIObjectInfo)
        p = e.get_property(0)
        self.assertTrue(e, self.gir.GIPropertyInfo)
        repr(p)

    def test_constantinfo(self):
        c = self._get_gtk(b"STOCK_ABOUT")
        self.assertTrue(isinstance(c, self.gir.GIConstantInfo))
        repr(c)

    def test_typeinfo(self):
        fi = self.repo.find_by_name(b"Gtk", b"get_major_version")
        self.assertTrue(isinstance(fi, self.gir.GICallableInfo))
        rt = fi.get_return_type()
        self.assertTrue(isinstance(rt, self.gir.GITypeInfo))

        fi = self.repo.find_by_name(b"Gtk", b"init")
        self.assertTrue(isinstance(fi, self.gir.GICallableInfo))
        argv = fi.get_arg(1)
        repr(argv)

    def test_typetag(self):
        self.failIf(self.gir.GITypeTag(18).is_basic)
        self.failUnless(self.gir.GITypeTag(21).is_basic)
        self.failUnless(self.gir.GITypeTag(10).is_basic)


class GIInfoCTypesTest(_GIInfoTest):
    from pgi.clib import gir

    def test_vfuncinfo(self):
        i = self._get_gtk(b"Editable")
        self.assertTrue(isinstance(i, self.gir.GIInterfaceInfo))
        for v in i.get_vfuncs():
            self.assertTrue(isinstance(v, self.gir.GIVFuncInfo))
            repr(v)

    def test_signalinfo(self):
        i = self._get_gtk(b"Editable")
        self.assertTrue(isinstance(i, self.gir.GIInterfaceInfo))
        for v in i.get_signals():
            self.assertTrue(isinstance(v, self.gir.GISignalInfo))
            repr(v)


class GIInfoCFFITest(_GIInfoTest):
    from pgi.cffilib import gir