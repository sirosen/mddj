from mddj._internal import _cached_methods


def test_cached_method_simple_case():
    class Foo:
        @_cached_methods.cached_method
        def bar(self):
            return object()

    obj = Foo()
    p = obj.bar()
    q = obj.bar()
    assert p is q


def test_cached_method_distinguishes_different_methods():
    # this test would fail if the method or method name were not injected into the key
    class Foo:
        @_cached_methods.cached_method
        def bar(self):
            return object()

        @_cached_methods.cached_method
        def baz(self):
            return object()

    obj = Foo()
    p = obj.bar()
    q = obj.baz()
    assert p is not q


def test_cached_method_distinguishes_different_calls():
    class Foo:
        @_cached_methods.cached_method
        def bar(self, x, y, z):
            return object()

    obj = Foo()

    x1 = obj.bar(1, 2, 3)
    y1 = obj.bar(2, 3, 4)

    assert x1 is not y1

    # shuffle params and use kwargs
    x2 = obj.bar(1, 2, z=3)
    y2 = obj.bar(z=4, y=3, x=2)

    assert x2 is not x1
    assert y2 is not y1

    # but in the same order, with kwargs, things match
    x3 = obj.bar(1, 2, z=3)
    assert x3 is x2
    y3 = obj.bar(z=4, y=3, x=2)
    assert y3 is y2
