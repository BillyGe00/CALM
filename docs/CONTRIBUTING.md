# Contributing

Thank you for your interest in contributing to CALM. This guide explains how to propose changes, add tests, and extend the benchmark.

1. Code style and tests

 - Follow existing code style and use type hints where practical.
 - Add unit tests for core reward logic or new environment features.

2. Adding tasks / data

 - Data files live under `calm_bench/envs/calendar/data/`.
 - Add persona entries to `personas.json`, baseline schedules to `calendars.json`, task prompts to `scheduling_requests.json`, and perturbations to `perturbations.json`.
 - Add a corresponding `Task` entry in one of `tasks_*.py` to exercise the new scenario.

3. Pull requests

 - Fork the repository, create a feature branch, and open a PR describing your changes.
 - Include examples or small reproducible runs demonstrating the effect of your change (optional but helpful).

4. Documentation

 - Update `README.md` and docs/ if you add major features or new evaluation dimensions.
