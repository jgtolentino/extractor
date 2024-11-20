from src.review import SystematicReview
from src.config import load_config, ConfigError
import logging
import sys

def setup_logging(log_level: str) -> None:
    """Configure logging based on environment"""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )

def main():
    try:
        # Load configuration
        config = load_config()
        
        # Setup logging
        setup_logging(config.log_level)
        
        # Initialize systematic review with configuration
        review = SystematicReview(config.user_email)
        
        # Example search across all databases
        query = "machine learning AND systematic review"
        review.search_databases(
            query=query,
            max_results=50,
            include_cochrane=True,
            include_clinicaltrials=True
        )
        
        # Export results
        review.export_results(format='csv')
        logging.info("Search completed and results exported successfully")
        
    except ConfigError as e:
        logging.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()