---
name: AetherVane Build & Teaching Plan
overview: Build the complete AetherVane IoT energy monitoring + automated load-shedding system (ESP32 + Django + Vue.js) in 6 phases over ~15 months (to March 2027), with every component explained in plain language for a beginner, tied to thesis chapters, and designed to scale up later. The student co-builds and learns each piece before moving on.
design:
  architecture:
    framework: vue
    component: shadcn
  styleKeywords:
    - Dark Mode
    - Glassmorphism
    - Energy Control Center
    - Premium Dashboard
    - Glowing Gauges
    - Gradient Charts
    - Micro-animations
    - Responsive Grid
  fontSystem:
    fontFamily: Montserrat / Source Sans Pro
    heading:
      size: 28px
      weight: 700
    subheading:
      size: 18px
      weight: 600
    body:
      size: 14px
      weight: 400
  colorSystem:
    primary:
      - "#00D4FF"
      - "#0A84FF"
    background:
      - "#0A0E27"
      - "#141B3D"
      - "#1A2142"
    text:
      - "#FFFFFF"
      - "#A0AEC0"
      - "#E2E8F0"
    functional:
      - "#00E676"
      - "#FF3D71"
      - "#FFB800"
todos:
  - id: phase1-vane-node
    content: Build Vane Node hardware + MicroPython firmware (sensors, relays, Wi-Fi POST, local fallback) with plain-language explanations of each electronic component and design choice
    status: completed
  - id: phase2-backend-db
    content: Build Django REST backend with MySQL schema, JWT auth, multi-tenant RBAC, device registration, and telemetry ingestion endpoint /api/v1/telemetry/ingest/
    status: completed
    dependencies:
      - phase1-vane-node
  - id: phase3-dsl-engine
    content: Implement Dynamic Shedding Logic engine with 4-tier relay shedding thresholds, hysteresis protection, and alert logging — explain algorithm with analogies and prepare defense Q&A for it
    status: completed
    dependencies:
      - phase2-backend-db
  - id: phase4-frontend
    content: "Build Vane Central Vue.js dashboard with dark-mode glassmorphism design: live gauges, multi-site selector, relay toggle controls, Chart.js analytics, alert feed"
    status: completed
    dependencies:
      - phase2-backend-db
  - id: phase5-integration
    content: "Run end-to-end integration testing: simulate battery voltage drops to verify DSL triggers relays, test multi-tenant isolation, security audit, use [code-explorer:code-explorer] to verify API contract alignment across all layers"
    status: completed
    dependencies:
      - phase3-dsl-engine
      - phase4-frontend
  - id: phase6-thesis-defense
    content: Write thesis chapters mapping each system layer to the problem statement, compile plain-language glossary, prepare panel Q&A with anticipated challenges, use [skill:docx] to generate formatted thesis and defense documents, and document scalability roadmap for future industrial version
    status: completed
    dependencies:
      - phase5-integration
---

## User Requirements

The user wants a single comprehensive technical report document that consolidates all the plain-language explanations, analogies, and design choice rationales that were embedded as code comments during the AetherVane build phases. The document must serve two purposes: (1) reference material for academic reports, and (2) personal study material for understanding and defending the project.

## Product Overview

A standalone Markdown report document organized by build phase (Phase 1 through Phase 5), extracting every beginner-friendly explanation from the codebase into a structured, readable format. A complete beginner should be able to read this report alone and understand the entire project well enough to explain it back.

## Core Features
- Title page with project info (name, author, institution, timeline)
- Table of contents
- Executive summary of the system
- Phase-by-phase sections with all term definitions, analogies, and design rationale
- Glossary of all technical terms at the end
- Scalability roadmap section

## Tech Stack Selection
- Document format: Markdown (.md) — universal, readable in any editor, convertible to Word/PDF later
- No code execution required — this is a pure documentation extraction and organization task

## Implementation Approach
The task is to create one Markdown file (`AetherVane_Technical_Report.md`) that extracts and reorganizes the plain-language explanations already present as code comments across all project files. The approach is:

1. **Extract** all explanations from the 5 firmware files, ~10 backend files, ~7 frontend files, and the integration findings
2. **Organize** them by build phase (Phase 1: Vane Node, Phase 2: Aether Core, Phase 3: DSL Engine, Phase 4: Vane Central, Phase 5: Integration)
3. **Structure** each phase section with sub-sections per component/module, preserving the original analogies and term definitions verbatim where possible
4. **Add** a glossary section consolidating all defined terms alphabetically
5. **Add** a scalability roadmap section explaining how the school-project version can grow into an industrial version

No new code is written. No existing code is modified. The report is purely derived from existing code comments and the known integration findings from the previous code-explorer verification.

## Implementation Notes
- Preserve analogies exactly as they appear in code comments (e.g., water tank analogy for DSL, apartment building for multi-tenancy, thermostat for hysteresis, stethoscope for CT clamp)
- Include the design choice rationale explanations (e.g., "why not connect ESP32 directly to appliances", "why average ADC readings", "why ADC2 pins are avoided")
- Include the Phase 5 integration findings: API contract alignment results, auth scheme divergence explanation, and the `mac` vs `device_id` bug fix
- The report should be self-contained — readable without access to the source code

## Directory Structure

```
AetherVane/
├── AetherVane_Technical_Report.md  # [NEW] Comprehensive technical report document
├── vane_node/                       # (existing, unchanged — source of Phase 1 explanations)
├── aether_core/                     # (existing, unchanged — source of Phase 2-3 explanations)
├── vane_central/                    # (existing, unchanged — source of Phase 4 explanations)
└── README.md                        # (existing, unchanged)
```

Only one new file is created. No existing files are modified.

## Key Code Structures
Not applicable — this is a documentation task with no new code interfaces or type definitions.
