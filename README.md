# Systematic Review Extraction System

A Python-based system for automating systematic review data extraction from multiple academic databases including PubMed, Cochrane Library, and ClinicalTrials.gov.

## Features

- 🔍 Multi-database search (PubMed, Cochrane, ClinicalTrials.gov)
- 📊 Automated metadata extraction
- 📈 Statistical analysis and meta-analysis tools
- 🔄 Data validation and quality checks
- 📑 Export to Excel and CSV formats

## Setup

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd systematic-review-extractor
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
```

Edit `.env` file with your credentials:
```ini
USER_EMAIL=your.email@example.com
API_KEY=your-api-key  # Optional
RATE_LIMIT=3
MAX_RETRIES=3
TIMEOUT=30
LOG_LEVEL=INFO
```

## Usage

### Basic Search

```python
from src.review import SystematicReview

# Initialize review
review = SystematicReview(email="your.email@example.com")

# Perform search
review.search_databases(
    query="machine learning AND systematic review",
    max_results=50,
    include_cochrane=True,
    include_clinicaltrials=True
)

# Export results
review.export_results(format='excel', filename='results')
```

### Statistical Analysis

```python
# Generate statistics
stats = review.generate_statistics()

# Access results
print(f"Total studies: {stats['summary']['study_counts']}")
print(f"Mean sample size: {stats['summary']['sample_sizes']['mean_sample_size']}")
```

### Data Validation

```python
# Validate data
validation = review.validate_data(generate_report=True)

# Check validation results
if validation['summary']['quality_score'] >= 80:
    print("Data quality is good")
else:
    print("Data quality issues found")
```

## API Documentation

### SystematicReview Class

Main class for systematic review operations.

```python
class SystematicReview:
    def __init__(self, email: str):
        """Initialize with NCBI email"""
        
    def search_databases(
        self, 
        query: str, 
        max_results: int = 100,
        include_cochrane: bool = True,
        include_clinicaltrials: bool = True
    ) -> None:
        """Search across multiple databases"""
        
    def export_results(
        self, 
        format: str = 'csv',
        filename: str = 'systematic_review_results'
    ) -> str:
        """Export results to file"""
```

### PaperMetadata Class

Data class for storing paper metadata.

```python
@dataclass
class PaperMetadata:
    title: str
    authors: List[str]
    doi: Optional[str]
    year: Optional[int]
    sample_size: Optional[int]
    study_type: Optional[str]
    full_text_links: List[str]
```

## Configuration

The system supports multiple environments through configuration files:

- `.env`: Base configuration
- `.env.development`: Development settings
- `.env.testing`: Testing settings
- `.env.production`: Production settings

## Troubleshooting

### Common Issues

1. **API Rate Limits**
   ```python
   # Adjust rate limiting in .env
   RATE_LIMIT=5  # Increase delay between requests
   ```

2. **Missing Dependencies**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

3. **Invalid Email**
   ```python
   # Ensure valid email for NCBI
   review = SystematicReview(email="valid.email@domain.com")
   ```

### Error Messages

- `ModuleNotFoundError`: Check virtual environment activation and dependencies
- `ConfigError`: Verify `.env` file configuration
- `ValueError: Invalid email format`: Provide valid email for NCBI access

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test category
pytest -m "pubmed"
pytest -m "metadata"

# Run with coverage
pytest --cov=src tests/
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## License

MIT License - See LICENSE file for details

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{systematic_review_extractor,
  title = {Systematic Review Extraction System},
  year = {2024},
  author = {Your Name},
  url = {repository-url}
}
```