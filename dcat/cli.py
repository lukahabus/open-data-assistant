"""Command-line interface for querying EU Data Portal."""
import argparse
import json
from typing import Optional
from .eu_data_portal import EUDataPortal

def format_dataset(dataset: dict, detailed: bool = False) -> str:
    """Format dataset for display.
    
    Args:
        dataset: Dataset metadata
        detailed: Whether to show detailed information
    
    Returns:
        Formatted dataset string
    """
    output = []
    output.append(f"Title: {dataset.get('dct:title', 'N/A')}")
    
    if detailed:
        output.append(f"ID: {dataset.get('@id', 'N/A')}")
        output.append(f"Description: {dataset.get('dct:description', 'N/A')}")
    
    publisher = dataset.get('dct:publisher', {}).get('foaf:name', 'N/A')
    output.append(f"Publisher: {publisher}")
    output.append(f"Modified: {dataset.get('dct:modified', 'N/A')}")
    
    return "\n".join(output)

def main():
    """Run the CLI interface."""
    parser = argparse.ArgumentParser(
        description="Search and explore datasets from the EU Data Portal"
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language query (if not provided, will prompt interactively)"
    )
    
    parser.add_argument(
        "-n", 
        "--limit",
        type=int,
        default=5,
        help="Maximum number of results to display"
    )
    
    parser.add_argument(
        "-d",
        "--detailed",
        action="store_true",
        help="Show detailed dataset information"
    )
    
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Save results to file"
    )
    
    args = parser.parse_args()
    
    # Initialize portal
    portal = EUDataPortal()
    
    # Get query if not provided
    query = args.query
    if not query:
        print("\nEnter your search query (e.g., 'climate change datasets from 2023'):")
        print("Type 'quit' to exit")
        
        while True:
            query = input("\nQuery> ").strip()
            if not query:
                continue
            if query.lower() == 'quit':
                break
                
            # Execute search
            print("\nSearching...")
            datasets = portal.search_datasets(query)
            
            if not datasets:
                print("No datasets found.")
                continue
            
            # Display results
            print(f"\nFound {len(datasets)} datasets:")
            for i, dataset in enumerate(datasets[:args.limit], 1):
                print(f"\n=== Result {i} ===")
                print(format_dataset(dataset, args.detailed))
                
                # Show distributions for detailed view
                if args.detailed:
                    dataset_id = dataset.get('@id')
                    if dataset_id:
                        distributions = portal.get_distributions(dataset_id)
                        if distributions:
                            print("\nDistributions:")
                            for dist in distributions:
                                print(f"- Format: {dist.get('format', 'N/A')}")
                                print(f"  URL: {dist.get('url', 'N/A')}")
    else:
        # Single query mode
        datasets = portal.search_datasets(query)
        
        if args.json:
            results = datasets[:args.limit]
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"Results saved to {args.output}")
            else:
                print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            if not datasets:
                print("No datasets found.")
            else:
                print(f"\nFound {len(datasets)} datasets:")
                for i, dataset in enumerate(datasets[:args.limit], 1):
                    print(f"\n=== Result {i} ===")
                    print(format_dataset(dataset, args.detailed))
                    
                    if args.detailed:
                        dataset_id = dataset.get('@id')
                        if dataset_id:
                            distributions = portal.get_distributions(dataset_id)
                            if distributions:
                                print("\nDistributions:")
                                for dist in distributions:
                                    print(f"- Format: {dist.get('format', 'N/A')}")
                                    print(f"  URL: {dist.get('url', 'N/A')}")
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        for dataset in datasets[:args.limit]:
                            f.write(format_dataset(dataset, True) + "\n\n")
                    print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()