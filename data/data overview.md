## Data Overview

* Baselines (existing calendars)
  1. recurring events
  2. one-time events
* Environment Constraints (immitate external constraints in openning hours and transportation time costs)
* Ground Truth (evaluation metrics)
* Personas (immitate real people in terms of lifestyles)
* Perturbations (emergencies that require calendar changes)
* User Requests (tasks to be completed by white agents)

## Q & A

* Shall we move **baseline_routine** from the **baseline** folder to **personas** folder? (sleep & meal & work & writing)
* Are we allowing natural language conversations between green and white agents? If not, then user request shall be made up of 2 types. Are we evaluating all aspects of a white agent based on one task or multiple tasks?
  1. ask the white agent to add events to an existing schedule according to natural language user request
  2. ask the white agent to adjust an exsiting schedule according to perturbation
* It seems that we cannot simply **randomly** choose one baseline, one persona, and one user request to be used as one data sample. We need to carefully choose which baseline, persona, and user request together make up the appropriate pair.
* Is it possible to simplify the data structure and information?
