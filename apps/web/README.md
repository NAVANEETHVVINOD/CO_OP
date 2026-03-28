# Co-Op Dashboard — Next.js Frontend

> The user interface for Co-Op Autonomous Company OS.  
> A dark‑theme dashboard that lets you monitor agents, approve proposals, upload documents, and chat with your AI workforce.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

---

## Overview

This is the frontend application for Co-Op. It communicates with the backend API via REST and Server‑Sent Events (SSE) to provide a real‑time view of your autonomous business.

- **Live agent activity** — See what each agent is doing, step by step.
- **Approval inbox** — Review and approve proposals, invoices, and other human‑in‑the‑loop actions.
- **Document management** — Upload, index, and search your portfolio files.
- **Chat with RAG** — Ask questions about your documents and get cited answers.
- **Cost tracker** — Monitor token usage and daily budgets.
- **Dark theme** — Designed for comfortable, long‑session use.

---

## Technology Stack

| Category | Tools |
|----------|-------|
| **Framework** | [Next.js 15](https://nextjs.org/) (App Router) |
| **Language** | TypeScript |
| **Styling** | Tailwind CSS, CSS variables (dark/light) |
| **State Management** | [Zustand](https://zustand-demo.pmnd.rs/) (client‑side) |
| **Data Fetching** | TanStack Query (optional, used for some pages) |
| **Real‑time** | Server‑Sent Events (SSE) via `EventSource` |
| **UI Components** | Radix UI primitives (Dialog, Tooltip, etc.) |
| **Icons** | Lucide React |
| **Build Tool** | Next.js built‑in compiler |

---

## Project Structure

```
apps/web/
├── public/                 # Static assets
├── src/
│   ├── app/                # Next.js App Router pages
│   │   ├── (app)/          # Authenticated routes (dashboard, chat, etc.)
│   │   ├── (auth)/         # Login / signup
│   │   └── layout.tsx      # Root layout
│   ├── components/         # Reusable UI components
│   │   ├── layout/         # Sidebar, top bar
│   │   ├── shared/         # EmptyState, PageHeader, StatusBadge
│   │   └── ui/             # Radix‑based components (button, card, dialog, etc.)
│   ├── hooks/              # Custom React hooks (useChat, etc.)
│   ├── lib/                # API client, utilities
│   ├── store/              # Zustand stores (chatStore, etc.)
│   └── types/              # TypeScript definitions (API responses)
├── .env.example            # Example environment variables
├── Dockerfile              # Multi‑stage build for production
├── next.config.ts          # Next.js configuration
├── tailwind.config.ts
├── package.json
└── README.md               # This file
```

---

## Running the Frontend

### Prerequisites
- Node.js 18+ and `pnpm` (recommended)
- Backend API running (see [main README](../../README.md))

### 1. Install Dependencies
```bash
pnpm install
```

### 2. Configure Environment
Copy the example environment file and adjust if needed:
```bash
cp .env.example .env.local
```

Default values:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
pnpm dev
```

The dashboard will be available at http://localhost:3000.

### 4. Build for Production
```bash
pnpm build
```

The static output will be in the `.next` directory. You can start it with:
```bash
pnpm start
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Base URL of the backend API | `http://localhost:8000` |

---

## Key Features

### Authentication
- Login page uses the backend `/v1/auth/token` endpoint.
- Token stored as `co_op_token` in `localStorage`.
- Automatic token refresh on 401 responses.

### Chat with Streaming
- Uses `EventSource` to receive token‑by‑token responses.
- Citations are displayed as cards below each message.
- Powered by the `useChat` hook and `chatStore`.

### Document Management
- Upload files (PDF, Word, text) → backend processes and indexes them.
- List, search, and delete documents from the dashboard.

### Approval Inbox
- Displays pending actions (proposals, invoices, etc.).
- Each item shows evidence of what the agent was doing and why.
- One‑click approve / reject.

### Agent Activity Feed
- Live feed of what each agent is currently doing.
- Integrates with the backend’s WebSocket or SSE endpoints.

### Cost Tracker (Stage 2+)
- Progress bar showing daily token usage vs budget.
- Fetches data from `/v1/costs` endpoint.

---

## Architecture Diagram (Frontend Perspective)

The frontend interacts with the backend API and consumes real‑time events as shown below:

```
┌─────────────────────────────────────────────────────────┐
│                   Next.js Dashboard                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │                User Interaction                 │   │
│  └─────────────────────────┬───────────────────────┘   │
│                            │                           │
│  ┌─────────────────────────▼───────────────────────┐   │
│  │            Zustand Stores (chatStore, etc.)     │   │
│  └─────────────────────────┬───────────────────────┘   │
│                            │                           │
│  ┌─────────────────────────▼───────────────────────┐   │
│  │            useChat, useDocuments, etc.          │   │
│  └─────────────────────────┬───────────────────────┘   │
│                            │                           │
│  ┌─────────────────────────▼───────────────────────┐   │
│  │            api.ts (fetch with token)            │   │
│  └─────────────────────────┬───────────────────────┘   │
└─────────────────────────────┼─────────────────────────┘
                              │ HTTP / SSE
┌─────────────────────────────▼─────────────────────────┐
│                    Backend API (FastAPI)              │
└───────────────────────────────────────────────────────┘
```

---

## Adding New Pages

1. Create a new folder under `src/app/(app)/` (e.g., `clients`).
2. Add a `page.tsx` file with the page component.
3. Optionally add a new menu item in `components/layout/AppSidebar.tsx`.
4. If the page needs data from the backend, add the corresponding API call in `lib/api.ts` and a Zustand store if needed.

---

## Styling

- Tailwind CSS is configured with a custom theme.
- Dark mode is controlled by a class `dark` on the `html` element. The default theme is dark.
- All colours are defined in `globals.css` as CSS variables, making them easy to override.

---

## Testing

Run tests (if any) with:
```bash
pnpm test
```

Currently there are no frontend tests; contributions are welcome.

---

## Contributing

Please refer to the main project’s [contributing guidelines](../../README.md#contributing). For frontend‑specific changes:

- Use TypeScript.
- Follow the existing component structure.
- Ensure the build passes (`pnpm build`).
- Test the page in both light and dark modes (light mode is not the default but should work).

---

## License

Apache License 2.0 – See [LICENSE](../../LICENSE) in the repository root.
