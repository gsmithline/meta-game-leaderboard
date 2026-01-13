"""Flatten nested per_agent results to a simple array format for DuckDB queries."""
import json
import sys

def flatten_results(input_file: str, output_file: str):
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Extract participants info - maps role names to AgentBeats UUIDs
    participants = data.get("participants", {})

    # Flatten: extract per_agent array from nested structure
    # Handle both formats:
    # 1. {"results": [{"per_agent": [...]}]} - wrapped format
    # 2. {"per_agent": [...]} - direct format from green agent
    flat_results = []

    if "results" in data and isinstance(data["results"], list):
        # Wrapped format: results array containing per_agent
        for result in data["results"]:
            per_agent = result.get("per_agent", [])
            for agent in per_agent:
                flat_results.append(agent)
    elif "per_agent" in data:
        # Direct format from green agent
        flat_results = data["per_agent"]

    # Map agent names to UUIDs using participants mapping
    # This ensures the leaderboard can link results to registered agents
    for agent in flat_results:
        agent_name = agent.get("agent_name", "")
        # Check if this agent name has a UUID in participants
        if agent_name in participants:
            agent["agent_name"] = participants[agent_name]

    # Output format with participants and results (AgentBeats convention)
    output = {
        "participants": participants,
        "results": flat_results
    }
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Flattened {len(flat_results)} agent results")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python flatten_results.py input.json output.json")
        sys.exit(1)
    flatten_results(sys.argv[1], sys.argv[2])
