# INTEGRATION VERIFICATION — SGP-CORE V2

**Date:** 2025-05-13

---

## System Integration Tests

### Test 1: Directory Structure

```python
def verify_directories():
    required = [
        'synthetic_universes/', 'null_models/', 'dynamics/',
        'pipeline/', 'metrics/', 'visualization/',
        'results/', 'archive_legacy/', 'obsidian_graph/'
    ]
    # Verify all exist and are accessible
    pass
```

### Test 2: Pipeline Integration

```python
def verify_pipeline():
    # synthetic_universes -> null_models -> pipeline -> metrics
    # -> visualization -> results
    pass
```

### Test 3: Null Model Integration

```python
def verify_null_models():
    # All 8 null types generate properly
    # Null comparison runs
    pass
```

### Test 4: Validation Runner Integration

```python
def verify_validation():
    # Phase A quick check -> Phase B full run
    # Pass/fail criteria work
    pass
```

---

## Cross-Component Check

| Component | Connects To | Test |
|-----------|-------------|------|
| synthetic_universes | null_models | Data passes through |
| null_models | pipeline | Null data feeds pipeline |
| pipeline | metrics | Output computes metrics |
| metrics | visualization | Metrics plot correctly |
| results | archive_legacy | Results archived |

---

## Status

**INTEGRATION SPECIFIED**  
Next: Execute integration tests