arquitetura do HULKs (que usa Rust)
# Architecture

Problem definition:
1. Lack of long-term vision and task decomposition.
2. Lack of an architecture definition.
3. Lack of documentation.
4. Lack of structure in code version management.

Ideally, the solution found should facilitate the transfer of knowledge to new students and allow them to integrate into the workflow quickly. This change should be implementable in the next 5 months, with the main goal of winning the next competition around November.

Some logical principles:
1. Simplicity, aiming to make onboarding and knowledge transfer easier.
2. Reusability.
3. Modularity, so that parts of the strategy can be tested independently. Or even for VSSS, for example.

middle: feedback loop, deliberate practice principles

principles
simplicity and onboarding
reusability (especially with VSSS)



Previous research:
- ROS is a giant hammer for a small nail
- C++ is dangerous for beginners (memory, UB, concurrency)
- Python is insufficient for real-time control
- However, Python has a huge structure for AI and NN.
- Rust solves all this without heavy frameworks


HULKs architecture (which uses Rust)
