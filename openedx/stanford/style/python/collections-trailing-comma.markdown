# Collections: Trailing Comma

## Expectation
- Add a trailing comma to all multiline collections
  - where syntactically allowed/identical

## Example

### Good
```python
words = [
    'foo',
    'bar',
]
```

```python
words = {
    'foo',
    'bar',
}
```

```python
words = [
    'foo': 1,
    'bar': 2,
]
```

### Bad
```python
words = [
    'foo',
    'bar'
]
```

```python
words = {
    'foo',
    'bar'
}
```

```python
words = [
    'foo': 1,
    'bar': 2
]
```

## Explanation
Trailing commas allow items to be added/removed from the collection
while minimizing the size of the changeset.
This reduces the chance of conflicts during merge [1].

Consider:

```diff
     'foo',
+    'bar',
 ]
```

```diff
     'foo',
-    'bar',
 ]
```

versus:

```diff
 words = [
-    'foo'
+    'foo',
+    'bar'
 ]
```

```diff
 words = [
-    'foo',
-    'bar'
+    'foo'
 ]
```

Consistently requiring trailing commas also helps to reduce the chance
of a class of logical errors. Consider:

```python
words = [
    'foo'
    'bar'
]
```

This snippet is syntactically vaild, but not the logic we intended.
In Python, consecutive strings are implicitly concatenated. So instead
of having a 2-item list with elements `'foo'` and `'bar'`, we have a
1-item list with the element `'foobar'`. By training our eyes (and
ideally even linters) to always expect a comma at the end of _every_
line, we reduce the risk of these bugs being introduced.

External Resources:
 1. TODO: link to explanation of changeset reduction (drop the diff)
