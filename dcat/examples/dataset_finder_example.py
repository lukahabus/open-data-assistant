"""Example script demonstrating EUDatasetFinder usage."""
from dcat.eu_dataset_finder import EUDatasetFinder
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run dataset finder examples."""
    finder = EUDatasetFinder()

    # Example 1: Find recent climate change datasets
    logger.info("\n=== Recent Climate Change Datasets ===")
    datasets = finder.find_recent_datasets(
        keywords=["climate", "change"],
        days_back=180,
        limit=5
    )
    
    if datasets:
        for dataset in datasets:
            print("\nDataset found:")
            print(f"Title: {dataset['title']}")
            print(f"Modified: {dataset.get('modified', 'N/A')}")
            print(f"Publisher: {dataset.get('publisher', 'N/A')}")
            print(f"URI: {dataset['dataset']}")
    else:
        print("No recent climate change datasets found.")

    # Example 2: Find CSV datasets about population
    logger.info("\n=== Population Statistics (CSV) ===")
    datasets = finder.find_datasets_by_format(
        format="csv",
        keywords=["population", "statistics"],
        limit=5
    )
    
    if datasets:
        for dataset in datasets:
            print("\nDataset found:")
            print(f"Title: {dataset['title']}")
            print(f"Distribution: {dataset.get('distribution', 'N/A')}")
            print(f"Format: {dataset.get('format', 'N/A')}")
            print(f"URI: {dataset['dataset']}")
    else:
        print("No CSV population statistics datasets found.")

    # Example 3: Find datasets by a specific publisher
    logger.info("\n=== Eurostat Datasets ===")
    datasets = finder.find_datasets_by_publisher(
        publisher_name="eurostat",
        limit=5
    )
    
    if datasets:
        for dataset in datasets:
            print("\nDataset found:")
            print(f"Title: {dataset['title']}")
            print(f"Modified: {dataset.get('modified', 'N/A')}")
            print(f"Publisher: {dataset['publisher']}")
            print(f"URI: {dataset['dataset']}")
    else:
        print("No Eurostat datasets found.")

    # Example 4: Get detailed information about a specific dataset
    # Only run this if we found at least one dataset above
    if datasets:
        logger.info("\n=== Dataset Details ===")
        dataset_uri = datasets[0]['dataset']
        details = finder.get_dataset_details(dataset_uri)
        
        if details:
            print("\nDetailed dataset information:")
            for key, value in details.items():
                print(f"{key}: {value}")
        else:
            print(f"Could not retrieve details for dataset: {dataset_uri}")

if __name__ == "__main__":
    main()