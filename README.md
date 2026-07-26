# Multi-Agent System

An autonomous multi-agent system that plans, routes, and implements code end-to-end.

## Architecture

**1. Planning Agent**
Decomposes the input task into an actionable to-do list.

**2. Router Agent**
Reads the to-do list and dispatches each item to the appropriate specialized agent (e.g., Developer, QA Engineer).

**3. Execution Agents**
Each specialized agent implements its assigned tasks using tools (read, write, code execution).

## Flow

```
Task → Planning Agent → To-Do List → Router Agent → [Developer Agent | QA Agent | ...] → Code
```
