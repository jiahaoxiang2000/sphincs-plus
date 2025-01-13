# SPHINCS+ Tests

This folder contains test files for the SPHINCS+ implementation. The tests verify the correct functioning of various components including WOTS+ operations.

## Test Structure

- `test_wots.py`: Tests for WOTS+ operations including:
  - Key generation
  - Signature generation and verification
  - Chain function operations
  - Base-w conversions

## Running the Tests

### Prerequisites

Make sure you have Python 3.7+ installed and the project's root directory is in your Python path.

### Running All Tests

From the project root directory:

```bash
python -m unittest discover tests
```

### Running Specific Test Files

To run WOTS+ tests only:

```bash
python -m unittest tests/test_wots.py
```

### Running Individual Test Cases

To run a specific test case:

```bash
python -m unittest tests.test_wots.TestWOTS.test_sign_verify
```

## Test Output

The tests will show:

- Number of tests run
- Any failures or errors
- Test execution time

## Adding New Tests

When adding new tests:

1. Create a new test file named `test_*.py`
2. Import the necessary modules
3. Create a class inheriting from `unittest.TestCase`
4. Add test methods starting with `test_`

## Common Issues

If you encounter import errors, ensure that:

1. The project root directory is in your Python path
2. All required dependencies are installed
3. The file structure matches the expected layout
