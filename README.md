# CALM (Calendar Agent for Life Management)

The CALM Scheduling Green Agent is an innovative Agentic AI evaluation framework (developed on the agentbeats platform) designed to rigorously assess calendar agents from the following aspects:
* **constraint satisfaction** (Does the schedule respect all hard constraints? ex. no time conflicts, mandatory events included, etc.)
* **persona-specific preference adherence** (Does the schedule reflect persona-specific preferences? ex. morning / night person, etc.)
* **work-life balance** (Does the schedule achieve a balanced ratio of work : rest : personal time = 10 : 8 : 6?)
* **dynamic re-planning disruption minimization** (Under changes, is the new schedule feasible, minimally disruptive or small edit distance from the original schedule, and stable across repeated trials?)
* (optional) **real-world feasibility** (Are scheduled activities possible given real-world constraints, ex. transportation time cost, opening hours, etc.)

CALM operates by feeding diverse synthetic personas and natural language scheduling requests into white scheduling agents, then score their outputs. We aim to enable comprehensive comparison and improvement of AI scheduling agents for work-life balance and practical usability.

The official agentbeats platform can be found here: https://github.com/agentbeats/agentbeats. For benchmark implementation onboarding, please check out docs/system_overview.md, then take a good look at some implemented agent examples located in the scenarios folder.
