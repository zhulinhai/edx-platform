# Collections: Multiline

## Expectation
- Define collections (lists, dictionaries, sets) with one item per line
- Indent lines by one level
  - don't align with the opening symbol: `(`/`[`/`{`

## Example

### Good
```python
words = [
    'foo',
    'bar',
]
```

### Bad
```python
words = ['foo', 'bar',]
```

```python
words = ['foo',
         'bar',]
```

## Explanation
Multiline collections are easier to manage (insert/remove)
when each item is on its own line.

This also reduces long lines, making the code easier to read.

Consider:

```diff
     'foo',
-    'bar',
 ]
```

```diff
     'bar',
+    'baz',
 ]
```

versus:

```diff
- words = ['foo', 'bar',]
+ words = ['foo',]
```

```diff
- words = ['foo', 'bar',]
+ words = ['foo', 'bar', 'baz',]
```

External Resources:
 1. http://edx.readthedocs.io/projects/edx-developer-guide/en/latest/style_guides/python_guidelines.html#breaking-long-lines
