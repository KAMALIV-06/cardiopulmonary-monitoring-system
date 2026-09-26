# Antigravity Global & Workspace Instructions

These instructions govern all agent pair-programming interactions:

## 1. Autonomous Execution Policy (No Unnecessary Approvals)
- **Routine / Basic Operations**: Execute directly and autonomously without asking the user for confirmation or waiting for submit prompts. This includes:
  - Installing dependencies (`npm install`, `pip install`, `pub get`)
  - Running builds, linters, and type checkers (`npm run build`, `tsc`, `pytest`, etc.)
  - Creating, modifying, and updating code files
  - Running smoke tests, test scripts, and diagnostic commands
  - Reading files and inspecting directories
- **Critical / Destructive Actions Only**: ONLY pause and request explicit user confirmation for truly destructive or irreversible actions:
  - Deleting entire projects or critical directories (`rm -rf`)
  - Dropping production databases or tables (`DROP TABLE`, `TRUNCATE`)
  - Force pushing to shared remote repositories (`git push --force`)
  - Modifying sensitive credentials or destroying cloud infrastructure resources
- **Follow Through**: Complete the entire multi-step task autonomously from start to finish without pausing midway.

## 2. Mandatory Task Time Estimates
- **For EVERY task or instruction**: Provide an upfront approximate time estimate for completion right at the start of your response:
  - Example: `⏱️ Estimated Time to Complete: ~2 minutes`
  - Keep estimates realistic and concise.

## 3. VS Code Developer Ergonomics
- The user is deeply familiar with Visual Studio Code.
- Always use standard VS Code formatting, directory conventions, and terminal workflows.
- Provide clickable file links using GitHub markdown (`file:///...`) format for easy opening in editors.
