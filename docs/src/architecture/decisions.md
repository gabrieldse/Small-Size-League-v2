# Architecture Decision Record (ADR)

## Problem Definition (dec 2025)
The project currently faces several critical challenges:
1. Lack of long-term vision and task decomposition.
2. Lack of an architecture definition.
3. Lack of documentation.
4. Lack of structure in code version management.

**Objective:** The chosen architecture must facilitate the transfer of knowledge to new students, allowing them to integrate into the workflow quickly. This structural shift must be completed and implementable within 5 months, with the primary goal of **winning the B series of the RoboCup 2026**.

## Principles
To meet our objectives, the architecture is designed around the following core principles:

- **Simplicity:** The system must be straightforward to navigate, making onboarding and knowledge transfer easy (critial for an undergraduate team).
- **Reusability:** Components should be written so they can be reused across different modules, particularly keeping VSSS (Very Small Size Soccer) in mind.
- **Modularity and Testability:** It is crucial that parts of the strategy and control loop can be isolated and tested independently. Even from hardware, SSL-vision and GameController.
- **Collaborative Development:** Contributions should be made collaboratively, ideally in pairs or small groups, to prevent knowledge silos and promote continuous knowledge sharing across the team.

## Decision Log

| Title | Description | Decider | Date |
| --- | --- | --- | --- |
| *Template* | *Brief description of the core decision and its rationale.* | *Name* | *YYYY-MM-DD* |
| Programming Language Choice | Transitioned to Python & C++. C++ for core high-performance parts, advantages of a typed and compiled language. Retained Python structure explicitly for AI, neural networks, and ease of onboarding. | ? | 12-2025 |
| Behavior Tree | Adopted Behavior Trees for the strategy logic to make the decision trees scalable, modular, and easier to debug for newcomers. | ? | 03-2026 |

*(Add new decisions here following the template above)*
