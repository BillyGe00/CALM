"""Real LLM agent that calls MCP tools using OpenAI.

This demonstrates how a real LLM agent uses the CALM environment tools
via OpenAI's function calling feature.

Usage:
    1. 在项目根目录创建 .env 文件，写入:
       OPENAI_API_KEY=your-api-key-here
    
    2. Run: python3.11 envs/tools/test_agent_openai.py
"""

import os
import sys
import json
from pathlib import Path

# Load .env file from project root
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from openai import OpenAI
from data_tools import get_persona, get_venue_hours


# Define tools for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_persona",
            "description": "Get detailed information about a specific persona including their preferences, constraints, and ideal schedule distribution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "persona_id": {
                        "type": "string",
                        "description": "The ID of the persona. Available options: 'graduate_student', 'working_parent', 'fitness_enthusiast'"
                    }
                },
                "required": ["persona_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_venue_hours",
            "description": "Query the operating hours of a venue on a specific day.",
            "parameters": {
                "type": "object",
                "properties": {
                    "venue_id": {
                        "type": "string",
                        "description": "The ID of the venue. Available options: 'gym', 'library', 'cafeteria', 'swimming_pool', 'grocery_store'"
                    },
                    "day": {
                        "type": "string",
                        "description": "The day of the week in lowercase: 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'"
                    }
                },
                "required": ["venue_id", "day"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a helpful scheduling assistant for the CALM (Calendar Agent for Life Management) system.

You have access to tools that can:
1. get_persona - Get information about a user's persona, including their preferences, constraints, and ideal schedule
2. get_venue_hours - Check when venues are open on specific days

When users ask about scheduling, personas, or venue hours, use these tools to get accurate information.
Always be helpful and provide clear, organized responses based on the tool results."""


def execute_tool(tool_name: str, args: dict) -> str:
    """Execute a tool and return the result as a string."""
    if tool_name == "get_persona":
        result = get_persona(**args)
    elif tool_name == "get_venue_hours":
        result = get_venue_hours(**args)
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    
    return json.dumps(result, indent=2)


def run_agent(client: OpenAI, query: str) -> str:
    """Run the OpenAI agent with a query."""
    print(f"\n{'='*60}")
    print(f"User Query: {query}")
    print(f"{'='*60}")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]
    
    # Step 1: Call OpenAI with tools
    print("\n🤖 Calling OpenAI...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )
    
    assistant_message = response.choices[0].message
    
    # Step 2: Check if the model wants to use tools
    if assistant_message.tool_calls:
        print(f"\n🔧 LLM decided to use {len(assistant_message.tool_calls)} tool(s):")
        
        # Add assistant message to conversation
        messages.append(assistant_message)
        
        # Execute each tool call
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"  → {function_name}({function_args})")
            
            # Execute the tool
            result = execute_tool(function_name, function_args)
            print(f"  ← Result received ({len(result)} chars)")
            
            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        # Step 3: Get final response from OpenAI
        print("\n💬 Getting final response from LLM...")
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        return final_response.choices[0].message.content
    else:
        # No tool calls, return direct response
        return assistant_message.content


def main():
    """Run the OpenAI agent with example queries."""
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("\n❌ Error: OPENAI_API_KEY not set!")
        print("\n请按以下步骤设置:")
        print(f"  1. 打开项目根目录的 .env 文件: {env_path}")
        print("  2. 把 your-api-key-here 替换成你的真实 API key")
        print("  3. 保存文件，重新运行此脚本")
        print("\n或者直接在终端运行:")
        print("  export OPENAI_API_KEY='你的真实key'")
        return
    
    print("\n" + "#" * 60)
    print("# CALM Real LLM Agent Demo (OpenAI)")
    print("# Using gpt-4o-mini with function calling")
    print("#" * 60)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Test queries
    queries = [
        "Tell me about the graduate student persona. What are their scheduling preferences?",
        "What time does the gym open on Saturday? Is it good for an early morning workout?",
        "I'm the working parent persona. When can I go to the library on Sunday?",
    ]
    
    for query in queries:
        try:
            response = run_agent(client, query)
            print("\n📋 Agent Response:")
            print("-" * 40)
            print(response)
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
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
            
            response = run_agent(client, user_input)
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

