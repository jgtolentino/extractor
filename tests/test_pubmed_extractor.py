import pytest
from src.extractors.pubmed import PubMedExtractor
from unittest.mock import patch, MagicMock

def test_pubmed_initialization(pubmed_extractor):
    """Test PubMed extractor initialization"""
    assert isinstance(pubmed_extractor, PubMedExtractor)
    assert pubmed_extractor.delay == 1

@patch('Bio.Entrez.esearch')
def test_pubmed_search(mock_esearch, pubmed_extractor):
    """Test PubMed search functionality"""
    # Mock response
    mock_response = MagicMock()
    mock_response.read.return_value = {
        'IdList': ['12345678', '87654321']
    }
    mock_esearch.return_value = mock_response
    
    # Test search
    results = pubmed_extractor.search("machine learning", max_results=2)
    assert len(results) == 2
    assert '12345678' in results
    
    # Verify API call
    mock_esearch.assert_called_once_with(
        db="pubmed",
        term="machine learning",
        retmax=2,
        usehistory="y"
    )

@patch('Bio.Entrez.efetch')
def test_fetch_details(mock_efetch, pubmed_extractor, mock_pubmed_response):
    """Test fetching article details"""
    # Mock response
    mock_handle = MagicMock()
    mock_handle.read.return_value = mock_pubmed_response
    mock_efetch.return_value = mock_handle
    
    # Test fetch
    article = pubmed_extractor.fetch_details('12345678')
    assert article['PMID'] == '12345678'
    assert article['TI'] == 'Machine Learning in Systematic Reviews: A Comprehensive Study'
    
    # Verify API call
    mock_efetch.assert_called_once_with(
        db="pubmed",
        id="12345678",
        rettype="medline",
        retmode="text"
    )

def test_parse_medline(pubmed_extractor, mock_pubmed_response):
    """Test MEDLINE format parsing"""
    parsed = pubmed_extractor._parse_medline(mock_pubmed_response)
    assert parsed['pmid'] == '12345678'
    assert 'Machine Learning' in parsed['TI']
    assert 'DOI' in parsed

@patch('Bio.Entrez.esearch')
def test_search_error_handling(mock_esearch, pubmed_extractor):
    """Test error handling during search"""
    mock_esearch.side_effect = Exception("API Error")
    results = pubmed_extractor.search("test query")
    assert results == []

@patch('Bio.Entrez.efetch')
def test_fetch_error_handling(mock_efetch, pubmed_extractor):
    """Test error handling during fetch"""
    mock_efetch.side_effect = Exception("API Error")
    result = pubmed_extractor.fetch_details("12345678")
    assert result == {}