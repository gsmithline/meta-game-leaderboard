"""Flatten nested per_agent results to a simple array format for DuckDB queries."""
import json
import sys

def flatten_results(input_file: str, output_file: str):
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Extract participants info
    participants = data.get("participants", {})

    # Flatten: extract per_agent array from nested structure
    flat_results = []
    results = data.get("results", [])
    for result in results:
        per_agent = result.get("per_agent", [])
        for agent in per_agent:
            flat_results.append(agent)

    # Output as bare JSON array - DuckDB can read this directly
    with open(output_file, 'w') as f:
        json.dump(flat_results, f, indent=2)

    print(f"Flattened {len(flat_results)} agent results")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python flatten_results.py input.json output.json")
        sys.exit(1)
    flatten_results(sys.argv[1], sys.argv[2])
