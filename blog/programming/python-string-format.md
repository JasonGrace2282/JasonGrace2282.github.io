# Formatting Strings in Python

```{post} March 18, 2025
---
tags: python
category: coding
---
```

[PEP-750](https://peps.python.org/pep-0750/) is quite close to being accepted - introducing yet
another way to interpolate and format strings. In this post,
we go through all the different ways of formatting strings in
Python, to get an idea of how string interpolation evolved to
where it is now. We'll start off with a formatting style
introduced at the birth of python, all the way to a PEP
for a brand new feature for string formatting!

## Percent Formatting
Stolen from the C programming language, python supports the following
syntax:
```py
>>> 'I said %s to you %d times!' % ('hello', 3)
'I said hello to you 3 times!'
```
Here, `%s` is replaced by the string `"hello"`, and `%d` is replaced
by the integer `3`. There are more qualifiers taken from the C
function `sprintf`, but in general this style of formatting
shouldn't be used because it has a lot of weird quirks.

## Percent Formatting Pt. 2
The younger sibling of percent formatting allows named values,
and is actually used often in python code (mainly due to `logging.basicConfig`).
It looks like this:

```py
>>> info = {'word': 'hello', 'num': 3}
>>> 'I said %(word)s to you %(num)d times!' % info
'I said hello to you 3 times!'
```
In here, `%(word)s` is replaced by `info["word"]`, and the trailing `s` means
it formats it as a string. In a similar manner, `%(num)d` is replaced
by `info["num"]`, which must be an integer due to the trailing `d` in `%(num)d`.

More information about this style of formatting can be found [here](https://docs.python.org/3/library/stdtypes.html#old-string-formatting)


## `string.Template`
[PEP-292](https://peps.python.org/pep-0292/) in Python2 was the first attempt to fix the
`%`-formatting madness, without requiring any syntax changes. It introduced
the class `string.Template`, which can be used as follows
```py
>>> from string import Template
>>> s = Template('${name} was born in ${country}')
>>> s.substitute(name='Guido', country='the Netherlands')
'Guido was born in the Netherlands'
```
If you are familar with shell scripting, this looks remarkably similar!
In fact, [it was straight up stolen from shell scripting](https://peps.python.org/pep-0292/#why-and-braces)!

In this method, `$` is the beginning of an identifier, which is replaced
by the corresponding keyword argument. For example, with `${name}`,
the identifier is `name`, and when calling `substitute(name='Guido')`
that whole string is replaced by `Guido`.

```{note}
As you may expect from shell scripting, both `${name}` and `$name`
work. However, unlike shell scripting, an undefined identifier
will raise an exception instead of being an empty string.
If you would like you avoid an exception, using `safe_substitute`
will retain the identifier in the string if it isn't passed in.
```

## `str.format`
The release of Python 3.0 introduced the revolutionary method `str.format` (which
was later backported to Python 2.6), which just about changed the way string formatting
was done. Instead of hardcoding the type (as with `%` formatting), or having to use
a cumbersome library, one could just format any object with a simple method. It looks
like this:

```py
>>> 'Hello {}, are you {}?'.format('Bob', 'doing well')
'Hello Bob, are you doing well?'
```
Here, the first `{}` is replaced by `Bob`, and the second `{}` is replaced
by `doing well`. Of course, if we wanted to flip the order, we could
add numbers:

```py
>>> 'Hello {1}, are you {0}?'.format('Bob', 'doing well')
'Hello doing well, are you Bob?'
```
Here, `{0}` is replaced by the 0th argument to `format`, or `Bob`. Likewise, `{1}`
is replaced by `doing well`.

We can even go so far as to access attributes!
```py
>>> 'My name is {0.name}'.format(open('out.txt', 'w'))
'My name is out.txt'
```
There is even one more syntax for `str.format`:

```py
>>> 'My name is {name}'.format(name='Hercule')
'My name is Hercule'
```
where the formatting arguments can be passed as keyword arguments to `str.format`.

In addition to easily formatting objects of any time, the introduction of `str.format`
also lead to the creation of formatters for objects (see [PEP-3101](https://peps.python.org/pep-3101/)).
This allowed easy formatting like
```py
>>> import math
>>> "{:.2f}".format(math.pi)
'3.14'
```
where in this case, `pi` was formatted to be 2 decimal points. Users could even create
their own formatting (see `__format__` in [PEP-3101](https://peps.python.org/pep-3101/))!

````{tip}
You can even automatically call functions like `repr` inside `str.format`!
```py
>>> s = 'Hello World!'
>>> 'User input: {!r}'.format(s)
'user input: "Hello World!"'
```
In this case, `!r` corresponds to `repr`. There are others: `!a` corresponding to ascii
and `!s` corresponding to `str`. These are also useful in conjunction with `=`: see the
f-string section for more information.
````


## f-strings
In an attempt to handle the verbosity of `string.Template`, the inadequacies of `%`-formatting,
and the verbosity of `str.format`, Python 3.6 introduced [f-strings](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals)
([PEP-498](https://peps.python.org/pep-0498/)),
a concise way to construct strings. This was the first change in the python grammer for string
interpolation since the release of the language! It looks like this:

```py
>>> name = 'Harold'
>>> f'My name is {name}'
'My name is Harold'
```
Notice the prefix of `f` before the string: that's what tells python to interpolate the string.
As with `str.format`, we can use the `__format__` protocol to format stuff nicely:
```py
>>> import math
>>> f'pi is approximately {math.pi:.2f}'
'pi is approximately 3.14'
```
F-strings also make a variety of things nicer:
```py
>>> name = 'Joe'
>>> f'{name = !r}'
'name = "Joe"'
```

````{tip}
It doesn't make a difference if you use a lowercase or a capital `f` for f-strings!
```py
>>> s = "hi"
>>> f'Say {s}!'
'Say hi!'
>>> F'Say {s}!'
'Say hi!'
```
````

## t-strings
`t`-strings are the first string prefix that don't actually create a string (except for `b`
for bytes)! The goal of `t`-strings ([PEP-750](https://peps.python.org/pep-0750/)) is to
introduce a way to create template strings that can be processed later.
For example, the following would create an instance of a class called `Template`
(not to be confused with `string.Template`):

```py
>>> template = t"Hello {world}!"
```
This template class has access to all the strings (in this case `("Hello ", "!")`),
and all of the interpolated values. The interpolated values
are an instance of the `Interpolation` type, which looks something like this:

```py
class Interpolation:
    value: object
    expr: str
    conv: Literal["a", "r", "s"] | None
    format_spec: str
```
Here, `value` is the evaluated interpolation, `expr` is the raw expression (`world` in our example),
`conv` is whether `!r`, `!s`, etc. were used, and `format_spec` is the format string
to be passed to `__format__`.

The authors of the PEP give several examples of where this could be useful, all of which seem
very useful! For example, preventing [Cross Site Scripting Attacks (XSS)](https://en.wikipedia.org/wiki/Cross-site_scripting)
can be done rather easily with an `html` function that takes a template:

```py
>>> evil = '<script>alert("evil")</script>'
>>> template = t'<p>{evil}</p>'
>>> html(template)
'<p>&lt;script&gt;alert("evil")&lt;/script&gt;</p>'
```

I highly recommend checking out the PEP for more examples!
