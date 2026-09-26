---
description: Autonomous command execution, critical-only approval, and upfront task time estimates
trigger: always_on
---

# User Execution Rules

1. **Autonomous Execution**:
   - For all basic commands, builds, tests, and code generation, execute them directly without prompting for permission.
   - Only ask for permission in critical cases (destructive deletions, dropping tables, formatting).
   - Complete tasks end-to-end without pausing in the middle.

2. **Upfront Task Time Estimates**:
   - For every task, output an upfront estimated completion time (e.g., `⏱️ Estimated Time: ~2-3 minutes`).

3. **VS Code Environment**:
   - Structure solutions, configs, and commands to align with VS Code conventions.
