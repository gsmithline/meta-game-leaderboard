"""
Test queries from queries.json file against result JSON files
"""
import json
import duckdb
import argparse
from pathlib import Path

# Get root directory (parent of tests/)
ROOT_DIR = Path(__file__).parent.parent

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description='Test DuckDB queries against result JSON files and validate leaderboard requirements'
)
parser.add_argument(
    '--queries',
    type=str,
    default=str(ROOT_DIR / "tests" / "queries.json"),
    help='Path to queries JSON file (default: tests/queries.json)'
)
parser.add_argument(
    '--results-dir',
    type=str,
    default=str(ROOT_DIR / "results"),
    help='Directory containing result JSON files (default: results/)'
)
args = parser.parse_args()

queries_path = Path(args.queries)
results_dir = Path(args.results_dir)
results_pattern = str(results_dir / "*.json")

print(f"Testing queries from {queries_path.relative_to(ROOT_DIR) if queries_path.is_relative_to(ROOT_DIR) else queries_path}...")
print(f"Against results in {results_dir.relative_to(ROOT_DIR) if results_dir.is_relative_to(ROOT_DIR) else results_dir}/")
print("="*60)

# Validate paths exist
if not queries_path.exists():
    print(f"ERROR: Queries file not found: {queries_path}")
    exit(1)

if not results_dir.exists():
    print(f"ERROR: Results directory not found: {results_dir}")
    exit(1)

# Load queries
with open(queries_path, 'r', encoding='utf-8') as f:
    queries = json.load(f)

print(f"Loaded {len(queries)} queries\n")

# Create DuckDB connection and load data
conn = duckdb.connect()
conn.execute(f"CREATE TABLE results AS SELECT * FROM read_json('{results_pattern}')")

success = []
failed = []
warnings = []

for query_info in queries:
    try:
        result = conn.sql(query_info['query'])
        rows = result.fetchall()
        columns = [desc[0] for desc in result.description]

        # Check if 'id' is the first column (required for leaderboard)
        if columns and columns[0] != 'id':
            warning_msg = f"First column is '{columns[0]}', but 'id' must be the first column"
            warnings.append((query_info['name'], warning_msg))
            print(f"⚠ {query_info['name']}")
            print(f"  WARNING: {warning_msg}")
            print(f"  Current columns: {columns}")
        else:
            success.append(query_info['name'])
            print(f"✓ {query_info['name']}")

        print(f"  Results: {len(rows)} rows")
        print(f"  Columns: {columns}")
        if len(rows) > 0:
            print(f"  Sample: {rows[:2]}")
    except Exception as e:
        failed.append((query_info['name'], str(e)))
        print(f"✗ {query_info['name']}: {str(e)[:100]}")

conn.close()

print("\n" + "="*60)
print(f"Results: {len(success)} passed, {len(warnings)} warnings, {len(failed)} failed")

if warnings:
    print("\n⚠ Queries with warnings (will fail on leaderboard):")
    for name, warning in warnings:
        print(f"  - {name}: {warning}")

if failed:
    print("\nFailed queries:")
    for name, error in failed:
        print(f"  - {name}: {error[:100]}")

# Exit with error code if there are failures or warnings
exit(len(failed) + len(warnings))
