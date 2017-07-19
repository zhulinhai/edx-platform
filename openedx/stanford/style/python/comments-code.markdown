# Comments - Code

## Expectation
- Don't commit commented code
  - Simply delete the code, adding any explanatory messaging to the
    commit message, as needed

## Example

### Bad
```python
# TODO: Uncomment this code after blah-blah-blah
```

## Explanation
Unused code is misleading and leads to false positives while searching
the codebase, wasting time.
The cruft also accumulates, as it's often never actually removed.

If we don't need it, we don't need it.
