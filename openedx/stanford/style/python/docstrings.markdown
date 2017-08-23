# Docstrings

## Expectation
- Use double-quotes instead of single quotes.
- Treat all docstrings as if they were multi-line.

## Example

### Good
```python
def foo():
    """
    Demonstrate a docstring
    """
    pass
```

### Good
```python
def foo():
    """
    Demonstrate a docstring

    with multiple lines
    """
    pass
```

### Bad
```python
def foo():
    '''
    Demonstrate a docstring
    '''
    pass
```

### Bad
```python
def foo():
    """ Demonstrate a docstring """
    pass
```

### Bad
```python
def foo():
    """ Demonstrate a docstring
    with multiple lines
    """
    pass
```

### Bad
```python
def foo():
    """ Demonstrate a docstring

    with multiple lines
    """
    pass
```

## Explanation
From PEP-257:
> Multi-line docstrings consist of a summary line just like a one-line
> docstring, followed by a blank line, followed by a more elaborate
> description. The summary line may be used by automatic indexing tools;
> it is important that it fits on one line and is separated from the
> rest of the docstring by a blank line.

### Double-quotes
From PEP-257:
> For consistency, always use """triple double quotes""" around docstrings.

### Multi-line strings
From PEP-257:
> Triple quotes are used even though the string fits on one line.
> This makes it easy to later expand it.

Taking this further, we can make it even easier to expand later
(and minimize the diff) by always treating docstrings as if they were
already multiline.

Consider:

```diff
     Demonstrate a docstring
+
+    with multiple lines
     """
```

versus:

```diff
 def foo():
-    """ Demonstrate a docstring """
+    """
+    Demonstrate a docstring
+
+    with multiple lines
+    """
     pass
```

External Resources:
 1. https://www.python.org/dev/peps/pep-0257/
