---
name: spawn-opencode
description: Launch an OpenCode sub-agent via Docker to execute a coding task on a specific repository and branch.
version: 1.0.0
author: Antigravity
license: MIT
metadata:
  hermes:
    tags: [delegation, opencode, docker, execution]
    related_skills: [subagent-driven-development, github-issues]
---

# Spawn OpenCode

## Overview

Use this skill to delegate coding tasks to an **OpenCode** sub-agent running in an ephemeral Docker container. OpenCode is highly efficient at terminal-based coding, running tests, and managing Git operations.

## When to Use

- When you have a clearly defined coding task (e.g., from an implementation plan).
- When the task requires modifying code, running tests, or performing Git operations.
- When you want to run multiple tasks in parallel (spawn one container per task).
- When you want to isolate the coding environment from the main Hermes instance.

## The Process

### 1. Prepare the Task

Ensure you have:
- A clear description of the task.
- The repository URL.
- The target branch name (e.g., `fix/issue-123`).

### 2. Launch OpenCode via Docker

Use the `terminal` tool to run the following command. Replace the placeholders with actual values.

```bash
docker run --rm \
  -e OPENAI_API_KEY=$MINIMAX_API_KEY \
  -e OPENAI_BASE_URL=https://api.minimax.io/v1 \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -v /tmp/opencode-work-$TASK_ID:/workspace \
  hermes-opencode:latest \
  --model openai/MiniMax-M2.7 \
  --task "$TASK_DESCRIPTION" \
  --repo "$REPO_URL" \
  --branch "$BRANCH_NAME"
```

**Environment Variables:**
- `OPENAI_API_KEY`: Use the Minimax API key.
- `OPENAI_BASE_URL`: Set to `https://api.minimax.io/v1` for Minimax support.
- `GITHUB_TOKEN`: Required for cloning private repos and pushing changes.

**Arguments:**
- `--model`: Explicitly use `openai/MiniMax-M2.7` (treated as OpenAI-compatible).
- `--task`: The specific coding task to perform.
- `--repo`: The GitHub repository URL.
- `--branch`: The branch to work on.

### 3. Monitor and Collect Results

OpenCode will report its progress in the terminal. Once it completes, it will push the changes to the branch and exit.

## Red Flags

- Don't pass vague tasks; be specific about what files to edit and what tests to run.
- Ensure `hermes-opencode:latest` image is built on the host.
- Always use `--rm` to clean up containers after completion.
- Use a unique volume path (e.g., `/tmp/opencode-work-$TASK_ID`) to avoid conflicts.
