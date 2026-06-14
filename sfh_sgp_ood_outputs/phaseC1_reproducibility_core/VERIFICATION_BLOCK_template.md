# VERIFICATION_BLOCK

## CLAIM
(One sentence. No interpretation. No metaphor.)

## RAW INPUT FILES
- file: path
  columns used: [col1, col2, ...]
  rows used: [which systems, which conditions]
- file: path
  columns used: [...]

## COMPUTATION PATH
```
step1: operation on column X → new value Y
step2: comparison of Y across rows → Z
step3: ...
```
Must be traceable from RAW INPUT to CLAIM with no gaps.

## OUTPUT FILES
- file: path, column, target value
- file: path, column, target value

## NULLS USED
- null name: description
- expected behavior under null
- observed behavior
- margin (difference / ratio)

## FAILURE MODES
- failure: condition that would make this claim false
- detected: yes/no/not checked
- severity if present

## WHAT WOULD INVALIDATE THIS CLAIM
(Exact condition, not vague.)

## WHAT REMAINS UNTESTED
(What has NOT been verified.)

## CONFIDENCE RATING
- computed / inferred / interpretive / unsupported
- reason for rating
