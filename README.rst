

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


