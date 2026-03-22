---
name: monitor-github-issues
description: Poll a GitHub repository for unassigned issues and create implementation tasks for Hermes.
version: 1.0.0
author: Antigravity
license: MIT
metadata:
  hermes:
    tags: [github, monitoring, automation, triage]
    related_skills: [spawn-opencode, github-issues]
---

# Monitor GitHub Issues

## Overview

Use this skill to automatically find work in a repository. Hermes will poll for new, unassigned issues and prepare them for processing by code sub-agents.

## The Process

### 1. List Recent Issues

Use the `terminal` tool with the `gh` CLI to list issues that match your criteria.

```bash
# List unassigned issues in a repo
gh issue list --repo agenthatchery/hermes-agent --state open --assignee ""
```

### 2. Triage and Selection

Review the list of issues. For each issue you want to process:
- Read the issue body to understand the request.
- Assess if it's a candidate for automated fix (e.g., bug fix, small feature).
- Assign the issue to yourself (Hermes) on GitHub.

```bash
# Assign an issue
gh issue edit <issue-number> --add-assignee "@me" --repo <repo-url>
```

### 3. Queue for Implementation

Once assigned, create a task (e.g., using `spawn_opencode` skill) to resolve the issue.

```bash
# Example: Spawn OpenCode for the issue
# task: resolves issue #123 (description: ...)
```

## Recommended Strategy

- **Polling Frequency**: Poll every 30-60 minutes or when idle.
- **Labels**: Look for specific labels like `autocode` or `bug` to filter tasks.
- **Limit Scale**: Start with 1-2 issues at a time to ensure quality.

## Red Flags

- Don't pick up issues that are already assigned to a human.
- Don't start work on issues with a `blocked` label.
- Always check the latest comments to see if a human has provided additional context.
