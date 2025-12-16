"""Simple test agent that calls MCP tools.

This demonstrates how an LLM agent can use the CALM environment tools.

Usage:
    1. Set OPENAI_API_KEY environment variable
    2. Run: python3.11 envs/tools/test_agent.py

Or run without API key for a simulated demo.
"""

import os
import json
from data_tools import get_persona, get_venue_hours


def simulate_agent_thinking(query: str) -> dict:
    """Simulate what an LLM agent would do when given a query.
    
    In a real implementation, this would be an LLM call that decides
    which tools to use based on the query.
    """
    query_lower = query.lower()
    
    # Simple rule-based simulation of agent reasoning
    if "persona" in query_lower or "user" in query_lower or "who" in query_lower:
        # Agent decides to use get_persona
        if "graduate" in query_lower or "student" in query_lower:
            return {"tool": "get_persona", "args": {"persona_id": "graduate_student"}}
        elif "parent" in query_lower or "working" in query_lower:
            return {"tool": "get_persona", "args": {"persona_id": "working_parent"}}
        elif "fitness" in query_lower:
            return {"tool": "get_persona", "args": {"persona_id": "fitness_enthusiast"}}
        else:
            return {"tool": "get_persona", "args": {"persona_id": "graduate_student"}}
    
    elif "gym" in query_lower or "library" in query_lower or "hours" in query_lower or "open" in query_lower:
        # Agent decides to use get_venue_hours
        venue = "gym"
        if "library" in query_lower:
            venue = "library"
        elif "cafeteria" in query_lower:
            venue = "cafeteria"
        
        day = "monday"  # default
        for d in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            if d in query_lower:
                day = d
                break
        
        return {"tool": "get_venue_hours", "args": {"venue_id": venue, "day": day}}
    
    return {"tool": None, "args": {}}


def execute_tool(tool_name: str, args: dict) -> dict:
    """Execute a tool by name with given arguments."""
    if tool_name == "get_persona":
        return get_persona(**args)
    elif tool_name == "get_venue_hours":
        return get_venue_hours(**args)
    else:
        return {"error": f"Unknown tool: {tool_name}"}


def format_response(query: str, tool_result: dict) -> str:
    """Format the tool result into a natural language response."""
    if "error" in tool_result:
        return f"I couldn't find that information. {tool_result['error']}"
    
    if "role" in tool_result:  # It's a persona
        p = tool_result
        return f"""Based on the persona information:

**{p['name']}** is a {p['role']}.

Key preferences:
- Chronotype: {p['preferences']['chronotype']}
- Wake time: {p['preferences']['wake_time']}
- Sleep time: {p['preferences']['sleep_time']}
- Work-life balance: {p['preferences']['work_life_balance']}
- Priorities: {', '.join(p['preferences']['priorities'])}

Constraints:
- Min sleep: {p['constraints']['min_sleep_hours']} hours
- Max work/day: {p['constraints']['max_work_hours_per_day']} hours
"""
    
    if "venue_id" in tool_result:  # It's venue hours
        v = tool_result
        return f"""The **{v['name']}** ({v['type']}) on {v['day'].capitalize()}:

- Opens: {v['hours']['open']}
- Closes: {v['hours']['close']}
{f"- Peak hours: {', '.join(v.get('peak_hours', []))}" if v.get('peak_hours') else ""}
{f"- Facilities: {', '.join(v.get('facilities', []))}" if v.get('facilities') else ""}
"""
    
    return json.dumps(tool_result, indent=2)


def run_agent(query: str) -> str:
    """Run the test agent with a query."""
    print(f"\n{'='*60}")
    print(f"User Query: {query}")
    print(f"{'='*60}")
    
    # Step 1: Agent thinks about what tool to use
    print("\n🤔 Agent thinking...")
    decision = simulate_agent_thinking(query)
    
    if decision["tool"] is None:
        print("  → No relevant tool found")
        return "I don't have a tool to help with that query."
    
    print(f"  → Decided to use: {decision['tool']}")
    print(f"  → With arguments: {decision['args']}")
    
    # Step 2: Execute the tool
    print("\n🔧 Executing tool...")
    result = execute_tool(decision["tool"], decision["args"])
    print(f"  → Got result (truncated): {str(result)[:100]}...")
    
    # Step 3: Format response
    print("\n💬 Formatting response...")
    response = format_response(query, result)
    
    return response


def main():
    """Run the test agent with example queries."""
    print("\n" + "#" * 60)
    print("# CALM Test Agent Demo")
    print("# This simulates how an agent would use the MCP tools")
    print("#" * 60)
    
    # Test queries
    queries = [
        "Tell me about the graduate student persona",
        "What are the gym hours on Monday?",
        "Who is the working parent user?",
        "When does the library open on Saturday?",
    ]
    
    for query in queries:
        response = run_agent(query)
        print("\n📋 Agent Response:")
        print("-" * 40)
        print(response)
    
    print("\n" + "#" * 60)
    print("# Demo Complete!")
    print("#" * 60)
    
    # Interactive mode
    print("\n💡 Try your own queries (type 'quit' to exit):\n")
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            if not user_input:
                continue
            
            response = run_agent(user_input)
            print("\n📋 Agent Response:")
            print("-" * 40)
            print(response)
            print()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()

