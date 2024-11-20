import pytest
from src.review import SystematicReview
from src.extractors.pubmed import PubMedExtractor
from src.extractors.paper_data import PaperMetadata

@pytest.fixture
def mock_pubmed_response():
    """Sample PubMed response data"""
    return """PMID- 12345678
TI  - Machine Learning in Systematic Reviews: A Comprehensive Study
AU  - Smith J
AU  - Johnson M
AU  - Williams R
DP  - 2023 Jan 15
AB  - Background: This study (n=500) evaluates machine learning approaches.
DOI - 10.1234/example.12345
PT  - Journal Article
PT  - Randomized Controlled Trial"""

@pytest.fixture
def mock_paper_metadata():
    """Sample paper metadata"""
    return PaperMetadata(
        title="Machine Learning in Systematic Reviews: A Comprehensive Study",
        authors=["Smith J", "Johnson M", "Williams R"],
        doi="10.1234/example.12345",
        year=2023,
        sample_size=500,
        study_type="RCT",
        full_text_links=["https://doi.org/10.1234/example.12345"]
    )

@pytest.fixture
def pubmed_extractor():
    """PubMed extractor instance"""
    return PubMedExtractor(email="test@example.com")

@pytest.fixture
def systematic_review():
    """Systematic review instance"""
    return SystematicReview(email="test@example.com")