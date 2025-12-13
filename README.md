# CALM (Calendar Agent for Life Management)

The CALM Scheduling Green Agent is an innovative Agentic AI evaluation framework (developed on the agentbeats platform) designed to rigorously assess calendar agents from the following aspects:
* **constraint satisfaction** (Does the schedule respect all hard constraints? ex. no time conflicts, mandatory events included, etc.)
* **persona-specific preference adherence** (Does the schedule reflect persona-specific preferences? ex. morning / night person, etc.)
* **work-life balance** (Does the schedule achieve a balanced ratio of work : rest : personal time = 10 : 8 : 6?)
* **dynamic re-planning disruption minimization** (Under changes, is the new schedule feasible, minimally disruptive or small edit distance from the original schedule, and stable across repeated trials?)
* (optional) **real-world feasibility** (Are scheduled activities possible given real-world constraints, ex. transportation time cost, opening hours, etc.)

CALM operates by feeding diverse synthetic personas and natural language scheduling requests into white scheduling agents, then score their outputs. We aim to enable comprehensive comparison and improvement of AI scheduling agents for work-life balance and practical usability.

The official agentbeats platform can be found here: https://github.com/agentbeats/agentbeats. For benchmark implementation onboarding, please take a look at some implemented agent examples located under the scenarios folder.

---

## Environment & Data (by Ayla)

### Data Files (`envs/data/`)

| File | Description |
|------|-------------|
| `personas.json` | 3 synthetic user personas with preferences, constraints, and ideal schedule distributions |
| `scheduling_requests.json` | 10 natural language scheduling requests for testing |
| `perturbations.json` | 9 schedule disruption scenarios (3 difficulty levels) |
| `external_constraints.json` | Venue hours, transportation schedules, and services |

### MCP Tools (`envs/tools/`)

Two tools are implemented and exposed via FastMCP:

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_persona` | Get detailed information about a specific persona | `persona_id`: string |
| `get_venue_hours` | Query venue operating hours on a specific day | `venue_id`: string, `day`: string |

**Note**: MCP server is created and tools are registered. Currently, the test uses direct function calls rather than MCP protocol for simplicity. The MCP server can be started with:

```bash
cd envs/tools && python3.11 server.py
```

### Testing

```bash
# Test tools directly (no API key needed)
cd envs/tools && python3.11 test_mcp.py

# Test with real LLM (requires OPENAI_API_KEY in .env)
cd envs/tools && python3.11 test_agent_openai.py
```

### Available Personas

- `graduate_student` - Alex Chen, PhD Student in Computer Science
- `working_parent` - Sarah Martinez, Marketing Manager and Mother of Two
- `fitness_enthusiast` - Mike Johnson, Software Engineer and Gym Trainer

### Available Venues

- `gym` - Campus Fitness Center
- `library` - University Library
- `cafeteria` - Student Cafeteria
- `swimming_pool` - Community Pool
- `grocery_store` - Fresh Market
