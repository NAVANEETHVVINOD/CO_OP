# 📖 Usage Guide

This guide explains how to manage and interact with your Co-Op Autonomous Company OS using the CLI and Desktop app.

## 🕹️ CLI Commands

The `coop` CLI is the primary management tool. Here are the most common commands:

### System Management
- `coop onboard setup`: Run the interactive configuration wizard.
- `coop gateway start`: Launch all backend Docker services.
- `coop gateway stop`: Shut down all backend services.
- `coop gateway status`: Check the health of all services.
- `coop doctor`: Run diagnostic checks on your environment.

### Data & Security
- `coop backup`: Create a snapshot of your database and object storage.
- `coop onboard hardware`: Re-run hardware detection for local LLM optimization.

### Agent Interaction
- `coop approve <id>`: Manually approve a pending action (Invoiced, Lead, etc.) from the terminal.
- `coop test`: Run the "Gold Path" E2E test to verify system integrity.

---

## 🖥️ Desktop Application

The Co-Op Desktop app provides a native experience with background monitoring.

### System Tray
- **Green Icon**: All systems healthy.
- **Red Icon**: One or more services are down.
- **Right-Click Menu**: Quick access to Start/Stop the gateway and "View Logs".

### Notifications
- The app polls for pending **Human-in-the-loop (HITL)** requests.
- You will receive a native OS notification when an agent requires your approval for a financial transaction or a proposal submission.

---

## 🌐 Dashboard (Web UI)

Access the dashboard at `http://localhost:3000` (or via the "Open Dashboard" menu in the desktop app).

- **Dashboard**: High-level overview of revenue, active projects, and agent status.
- **Agents**: Chat with your Lead Scout, Proposal Writer, or Finance Manager.
- **Approvals**: The HITL queue where you review and approve agent actions.
- **Projects**: Manage your active work and client communications.
- **Finance**: Track invoices, credits, and spending.

---

## 🤖 Working with Agents

1.  **Lead Scout**: Automatically finds potential business opportunities based on your profile.
2.  **Proposal Writer**: Drafts high-quality proposals using information from your RAG-stored documents.
3.  **Finance Manager**: Handles invoicing and payment tracking.

Always review agent outputs in the **Approvals** tab before they are sent to clients.
