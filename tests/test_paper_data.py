import pytest
from src.extractors.paper_data import PaperDataExtractor, PaperMetadata

@pytest.fixture
def paper_extractor():
    return PaperDataExtractor()

def test_extract_metadata(paper_extractor, mock_pubmed_response):
    """Test complete metadata extraction"""
    data = paper_extractor._parse_pubmed_response(mock_pubmed_response)
    metadata = paper_extractor.extract_metadata(data)
    
    assert isinstance(metadata, PaperMetadata)
    assert "Machine Learning" in metadata.title
    assert len(metadata.authors) == 3
    assert metadata.year == 2023
    assert metadata.sample_size == 500
    assert metadata.study_type == "RCT"

def test_validate_title(paper_extractor):
    """Test title validation"""
    valid_title = "Valid Title"
    assert paper_extractor._validate_title(valid_title) == valid_title
    
    with pytest.raises(ValueError):
        paper_extractor._validate_title("")
    
    with pytest.raises(ValueError):
        paper_extractor._validate_title("  ")

def test_extract_authors(paper_extractor):
    """Test author extraction"""
    data = {
        'AU': ['Smith J', 'Johnson M'],
        'FAU': ['Smith, John', 'Johnson, Mary']
    }
    authors = paper_extractor._extract_authors(data)
    assert len(authors) == 2
    assert 'Smith J' in authors

def test_extract_doi(paper_extractor):
    """Test DOI extraction"""
    data = {'DOI': '10.1234/example.12345'}
    doi = paper_extractor._extract_doi(data)
    assert doi == '10.1234/example.12345'
    
    # Test invalid DOI
    data = {'DOI': 'invalid-doi'}
    doi = paper_extractor._extract_doi(data)
    assert doi is None

def test_extract_year(paper_extractor):
    """Test publication year extraction"""
    # Test different date formats
    assert paper_extractor._extract_year({'DP': '2023'}) == 2023
    assert paper_extractor._extract_year({'DP': '2023/01/15'}) == 2023
    assert paper_extractor._extract_year({'DP': '2023 Jan 15'}) == 2023
    
    # Test invalid date
    assert paper_extractor._extract_year({'DP': 'invalid'}) is None

def test_extract_sample_size(paper_extractor):
    """Test sample size extraction"""
    text = "This study included n=500 participants"
    data = {'AB': text}
    assert paper_extractor._extract_sample_size(data) == 500
    
    # Test different formats
    assert paper_extractor._extract_sample_size({'AB': 'sample size of 300'}) == 300
    assert paper_extractor._extract_sample_size({'AB': 'enrolled 250 participants'}) == 250

def test_detect_study_type(paper_extractor):
    """Test study type detection"""
    # Test RCT detection
    assert paper_extractor._detect_study_type({'TI': 'A Randomized Controlled Trial'}) == 'RCT'
    
    # Test meta-analysis
    assert paper_extractor._detect_study_type({'TI': 'A Meta-Analysis'}) == 'Meta-Analysis'
    
    # Test unknown type
    assert paper_extractor._detect_study_type({'TI': 'A Study'}) is None

def test_extract_full_text_links(paper_extractor):
    """Test full text link extraction"""
    data = {
        'DOI': '10.1234/example.12345',
        'LID': 'https://example.com/paper'
    }
    links = paper_extractor._extract_full_text_links(data)
    assert len(links) == 2
    assert 'https://doi.org/10.1234/example.12345' in links