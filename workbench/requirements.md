# System Resource Monitor - Project Requirements Document

## 1. Project Overview

**Project Name:** System Resource Monitor (SRM)

**Purpose:** Develop a lightweight, cross-platform system resource monitoring tool that collects, analyzes, and reports on key system performance metrics in real-time.

**Target Users:** System administrators, DevOps engineers, developers, and power users who need visibility into system performance.

## 2. Project Scope

The tool will monitor critical system resources, log historical data, generate alerts on threshold violations, and present information through both a CLI dashboard and optional web interface.

## 3. Resources to Monitor (Selected)

The following system resources have been selected for monitoring based on their critical importance to system health and performance:

### ✅ Selected Resources:

| # | Resource | Rationale | Metrics Collected |
|---|----------|-----------|-------------------|
| 1 | **CPU** | Core processing unit; bottlenecks directly impact all system operations | Overall usage %, per-core usage, frequency, load average, temperature (if available) |
| 2 | **Memory (RAM)** | Essential for running processes; low memory causes swapping and degradation | Total, used, free, available, swap usage, cache/buffer |
| 3 | **Disk** | Storage health affects I/O performance and data availability | Usage per partition, I/O rates (read/write), disk space, inode usage |
| 4 | **Network** | Connectivity and throughput critical for distributed systems | Bytes sent/received, packets, errors, drops, active connections |
| 5 | **Processes** | Visibility into running workloads helps identify resource hogs | Top N processes by CPU/memory, process count, thread count, zombie processes |

### ❌ Resources NOT Included (with justification):
- **GPU** – Not universally available; can be added as future enhancement
- **Sensors (fan, voltage)** – Hardware-specific; low general utility
- **USB/Bluetooth devices** – Peripheral monitoring outside project scope
- **Power/Battery** – Mobile/edge specific; out of current scope

## 4. Functional Requirements

### FR1: Data Collection
- The system **SHALL** collect CPU, memory, disk, network, and process data at configurable intervals (default: 1 second).
- The system **SHALL** support collection intervals from 100ms to 60s.
- The system **SHALL** work on Linux, macOS, and Windows.

### FR2: Real-Time Display
- The system **SHALL** provide a terminal-based dashboard updating in real-time.
- The system **SHALL** display all five resource categories simultaneously.
- The system **SHALL** support color-coded indicators (green/yellow/red) based on thresholds.

### FR3: Alerting
- The system **SHALL** trigger alerts when configurable thresholds are exceeded.
- The system **SHALL** support alerts via console, log file, and webhook.
- The system **SHALL** prevent alert spam via configurable cooldown periods.

### FR4: Historical Data
- The system **SHALL** retain the last 24 hours of data in memory by default.
- The system **SHALL** optionally persist data to SQLite for long-term storage.
- The system **SHALL** allow exporting data to CSV/JSON.

### FR5: Process Management
- The system **SHALL** display top 10 processes by CPU and memory consumption.
- The system **SHALL** allow filtering processes by name.
- The system **SHALL** support optional process termination (with confirmation).

## 5. Non-Functional Requirements

### NFR1: Performance
- The monitor **SHALL** consume less than 2% CPU when idle.
- The monitor **SHALL** use less than 100MB of RAM.
- Data collection **SHALL NOT** block system operations.

### NFR2: Reliability
- The monitor **SHALL** auto-recover from collection errors.
- The monitor **SHALL** log all errors to a file with rotation.
- The monitor **SHALL** handle missing or inaccessible data gracefully.

### NFR3: Usability
- The monitor **SHALL** provide a clear, intuitive terminal interface.
- The monitor **SHALL** support keyboard shortcuts for common actions.
- The monitor **SHALL** include a help screen and configuration documentation.

### NFR4: Portability
- The monitor **SHALL** run on Linux, macOS, and Windows.
- The monitor **SHALL** be distributed as a single executable.
- The monitor **SHALL** have zero external runtime dependencies.

### NFR5: Security
- The monitor **SHALL** require no elevated privileges by default.
- The monitor **SHALL** sanitize all output to prevent injection.
- The monitor **SHALL** validate all configuration inputs.

## 6. Technical Requirements

### TR1: Technology Stack
- **Language:** Python 3.9+ (cross-platform compatibility)
- **Key Libraries:**
  - `psutil` – Cross-platform system info
  - `rich` – Terminal UI rendering
  - `asyncio` – Non-blocking data collection
  - `SQLite` – Optional data persistence

### TR2: Architecture
- **Collector Module:** Handles data acquisition for each resource
- **Storage Module:** Manages in-memory and persistent data
- **Alerting Module:** Evaluates thresholds and triggers alerts
- **UI Module:** Renders terminal dashboard
- **Config Module:** Manages user configuration

### TR3: Configuration
- Configuration via YAML file (`config.yaml`)
- Command-line argument overrides
- Environment variable support

## 7. Default Thresholds

| Resource | Warning | Critical |
|----------|---------|----------|
| CPU | > 70% | > 90% |
| Memory | > 80% | > 95% |
| Disk | > 80% | > 95% |
| Network Errors | > 10/min | > 50/min |
| Process Count | > 500 | > 1000 |

## 8. Deliverables

1. Executable monitoring tool
2. Configuration file with defaults
3. User documentation (README, usage guide)
4. Sample dashboard screenshots/output
5. Unit and integration tests (>80% coverage)

## 9. Out of Scope

- Distributed/multi-host monitoring (future enhancement)
- Cloud provider integrations
- Container orchestration metrics (use Prometheus for this)
- Application-level APM tracing

## 10. Success Criteria

- Successfully monitors all 5 selected resources on at least 3 OS platforms
- Runs continuously for 7+ days without crashes or memory leaks
- Resource overhead stays within NFR1 limits
- Users can identify top resource consumers within 5 seconds of viewing dashboard
