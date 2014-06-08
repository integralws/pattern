#!/usr/bin/env python

"""

>>> Pattern('/{a}').parse('/foo.html')
PatternResult(a='foo.html')

>>> Pattern('/{a}.html').parse('/foo.html')
PatternResult(a='foo')

Each substitution pattern tries to consume as much as possible by default

>>> Pattern('/{a}').parse('/a/b/c')
PatternResult(a='a/b/c')

Override the ``default_match`` class attribute to adjust this behavior

>>> class StrictPathPattern(Pattern):
...   default_match = r"[^/]*"  # Consume any non-slash character

>>> StrictPathPattern('/{a}').parse('/c/b/a')
Traceback (most recent call last):
 ...
ValueError: '/c/b/a' does not match pattern '/{a}'

>>> StrictPathPattern('/{a}/{b}/{c}').parse('/c/b/a').kwargs == dict(a="c", b="b", c="a")
True

>>> Pattern('/{0}bar').parse('/foobar')
PatternResult('foo')

Pattern matching works in reverse too.

>>> Pattern('/{root}/{branch}/{leaf}/{0}').replace('d', root="a", branch="b", leaf=3)
'/a/b/3/d'

>>> def my_callable(a, option='foo', beta=10):
...   return (a + '123', beta - 10, option)

>>> Pattern('/{0}/{beta}', beta=int).parse('/alpha/5').apply(my_callable)
('alpha123', -5, 'foo')

Adjacent matches will consume one character each until the last. This behavior
currently follows the behavior of the regular expression (.+?) and is subject to
change in future versions.

>>> my_pattern = Pattern('{0}{1}{a}')

>>> my_pattern.parse('123456')
PatternResult('1', '2', a='3456')

>>> my_pattern.parse('12')
Traceback (most recent call last):
 ...
ValueError: '12' does not match pattern '{0}{1}{a}'

>>> my_pattern.regex()
'^(?P<_0>.+?)(?P<_1>.+?)(?P<_a>.+?)$'

If necessary, regular expressions for each object can be added to the pattern's
``matches`` attribute.

>>> my_pattern.matches['a'] = r"[0-9]{2}"  # {a} matches exactly 2 digits

>>> my_pattern.parse('123456')
PatternResult('1', '234', a='56')

>>> my_pattern.parse('123')
Traceback (most recent call last):
 ...
ValueError: '123' does not match pattern '{0}{1}{a}'

"""

import re


class PatternResult(object):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def apply(self, function):
        return function(*self.args, **self.kwargs)

    def __repr__(self):
        return 'PatternResult({})'.format(', '.join([repr(arg) for arg in self.args] +
                                                    ['{}={!r}'.format(*item) for item in self.kwargs.items()]))


class Pattern(object):
    default_match = r".+?"
    prefix = '^'
    postfix = '$'

    def __init__(self, pattern_string, *arg_xformers, **transformers):
        self.pattern_string = pattern_string
        self.transformers = transformers
        self.transformers.update({i:v for i, v in enumerate(arg_xformers)})
        self.matches = dict()

    def match(self, matchobject):
        return r"(?P<_%s>%s)" % (matchobject.group(1), self.matches.get(matchobject.group(1), self.default_match))

    def regex(self):
        return self.prefix + re.sub(r"(?<!\\\{)\\\{(0|[_a-zA-Z1-9][_a-zA-Z0-9]*)\\\}",
                                   self.match, re.escape(self.pattern_string)) + self.postfix

    def parse(self, string):
        match = re.match(self.regex(), string)
        if not match:
            raise ValueError("%r does not match pattern %r" % (string, self.pattern_string))
        args, values = dict(), match.groupdict()
        for key in list(values):
            if key[0] == '_':
                try:
                    k, which = int(key[1:]), args
                except ValueError:
                    k, which = key[1:], values
                which[k] = self.transformers.get(k, lambda x:x)(values.pop(key))
            else:
                getattr(self, 'handle_%s' % key)(values.pop(key), args, values)
        args = [value for key, value in sorted(args.items())]
        return PatternResult(args, values)

    def replace(self, *args, **values):
        return self.pattern_string.format(*args, **values)


class PathPattern(Pattern):
    """Elements do not cross slash ("/") boundaries.

    >>> PathPattern('/{0}').parse('/a')
    PatternResult('a')

    >>> PathPattern('/{0}').parse('/a/b')
    Traceback (most recent call last):
     ...
    ValueError: '/a/b' does not match pattern '/{0}'

    """
    default_match = r"[^/]+"


class URLPattern(PathPattern):
    postfix = r"(?P<_query>\?.*)$"


if __name__ == '__main__':
    import doctest
    doctest.testmod()