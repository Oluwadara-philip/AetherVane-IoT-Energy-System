# PROJECT BLUEPRINT: Project AetherVane
**Official Thesis Title:** *Design and Implementation of IoT Multi-Tenant Energy Monitoring and Automatic Load-Shedding System Based on Django+Vue.js*  
**Author:** Oluwadara Philip Adetokunbo  
**Institution:** Chengdu Neusoft University, School of Software Engineering  
**Timeline:** Development & Testing (Now – March 2027) | Submission: March 2027 | Defense: April 2027  
**Total Budget:** < 500 RMB (~120 RMB estimated actual hardware cost)

---

## Section 1: Executive Summary & Problem Statement

### 1.1 The Core Problem
In regions with unstable power grids or remote off-grid solar deployments, hybrid power systems (Solar + Inverter + Battery Banks) frequently suffer from **deep discharge damage**. When grid power fails and heavy appliances (such as air conditioners or water heaters) continue drawing power unchecked, battery voltage drops below safe operational thresholds, destroying expensive energy storage equipment. Manual monitoring is unreliable and labor-intensive.

### 1.2 The Software Solution (AetherVane)
Project AetherVane is a **Multi-Tenant IoT Energy Monitoring and Automated Load-Shedding Platform**. It decouples the hardware edge from the cloud management tier via a secure 3-tier architecture. It allows multiple independent organizations to monitor their physical sites, track real-time power telemetry, remotely control electrical circuits, and execute **Dynamic Shedding Logic (DSL)** to protect batteries automatically when voltage drops.

---

## Section 2: System Constraints & Requirements

### 2.1 Constraints & Boundaries
* **Budget Limit:** Strictly under 500 RMB. (Actual component cost is ~120 RMB, purchased via Taobao).
* **Scope Boundary:** Hardware circuit design, PCB layouts, and sensor analog physics are treated strictly as an **external IoT Edge interface**. The primary focus (85%+) is software engineering: Django REST backend, Vue.js presentation layer, multi-tenant isolation, database design, and automated rule engines.
* **Network Assumptions:** Operates over standard 2.4GHz Wi-Fi with local firmware fallback logic if cloud connectivity is lost.

### 2.2 The 8 Core Software Functions
1. **Multi-Tenant Account & RBAC Engine:** JWT-based authentication managing Super Admin, Site Manager, and Viewer roles.
2. **Multi-Site & Spatial Hierarchy Management:** Organizational structure isolating data between tenants (`Organizations` $\rightarrow$ `Sites` $\rightarrow$ `Devices` $\rightarrow$ `Circuits`).
3. **Telemetry Ingestion Pipeline:** High-throughput Django REST endpoint (`/api/v1/telemetry/ingest/`) parsing incoming JSON payloads from edge nodes.
4. **Dynamic Load-Shedding Engine (DSL Rule Engine):** Automated background evaluation checking battery voltage against user-defined thresholds to trigger relay cutoffs.
5. **Real-Time Data Visualization Dashboard:** Vue.js interactive interface displaying live power meters, time-series charts, and status indicators.
6. **Remote Circuit Control & Manual Override:** Bidirectional REST commands allowing authorized users to flip remote relay switches instantly.
7. **Device Registration & Lifecycle Management:** Admin portal for generating hardware API tokens, tracking heartbeats, and detecting offline edge nodes.
8. **Automated Alerting & Audit Logging:** Persistent logging of user overrides, threshold breaches, and load-shedding events.

---

## Section 3: 3-Tier System Architecture & Data Flow