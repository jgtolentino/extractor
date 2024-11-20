# Systematic Review Test Suite

This test suite covers the core functionality of the systematic review extraction system.

## Test Structure

- `conftest.py`: Common fixtures and mock data
- `test_pubmed_extractor.py`: Tests for PubMed data extraction
- `test_paper_data.py`: Tests for paper metadata extraction and validation

## Running Tests

```bash
pytest tests/
pytest tests/ -v  # Verbose output
pytest tests/ -k "test_name"  # Run specific test
```

## Test Coverage

- PubMed API integration
- MEDLINE format parsing
- Metadata extraction
- Data validation
- Error handling

## Mock Data

The test suite includes mock responses for:
- PubMed API responses
- Paper metadata
- Various date formats
- Different study types

## Adding New Tests

1. Add fixtures to `conftest.py` if needed
2. Create new test file or add to existing ones
3. Follow naming convention: `test_*`
4. Include docstrings explaining test purpose