# Supplier Email Parser — Standalone Real GUI Implementation

This folder is now its own runnable project app. It does not depend on the root all-project dashboard at runtime.

## Run

```bash
./run_gui.sh
```

Windows:

```powershell
.\run_gui_windows.ps1
```

Default URL: `http://127.0.0.1:9157`

## What is inside this project folder

- `app/` — FastAPI backend for this project.
- `static/` — elegant browser GUI.
- `plugins/supplier-email-parser.json` — this project’s own feature/customization/input schema.
- `project_config.json` — readable copy of the same project-specific configuration.
- `data/` — local SQLite jobs, uploads, exports.
- `tests/` — verifies this project has a registered real local engine.

## Project-specific scope

- Domain: `Supply Chain / Procurement`
- Target user: `Domain operator, business owner, analyst, or team member who needs this workflow executed reliably.`
- Core job: Supplier thread → structured PO/procurement data
- Suite: `Supply Chain Suite`

## Deep features applied

- item/quantity/price extraction
- date normalization
- discrepancy detection
- PO draft
- supplier memory
- payment term extraction
- approval workflow

## Customization controls

- `execution_mode` — Execution mode (select)
- `currency` — currency (select)
- `units` — units (text)
- `supplier_profiles` — supplier profiles (select)
- `po_template` — PO template (text)
- `tolerance_rules` — tolerance rules (slider)
- `payment_terms` — payment terms (text)
- `approval_policy` — approval policy (text)
- `output_format` — output format (select)
- `language` — language (select)
- `privacy_mode` — privacy mode (select)
- `confidence_threshold` — Confidence threshold (slider)

## Input fields

- `supplier_thread` — Supplier thread (text) required
- `work_brief` — Work brief / source text / URL / instructions (textarea) required

## External data policy

The local deterministic core is real and executable. Live external systems are not simulated. If Shopify, ATS, ERP, OCR/STT, maps, SERP, market data, medical databases, tax/customs databases, or other live systems are required, this project reports the missing connector/API requirement instead of inventing data.

---

## Final UX/UI Layer

This project now uses the **Supply Chain Operations Desk** pattern.

**UX workflow:** Document/email intake → matching → discrepancy/risk → action/export

**Domain components:**
- Document matching board
- Shipment/procurement checklist
- Discrepancy table
- Supplier action panel
- Export package

**Quick actions:**
- Match documents
- Find discrepancies
- Prepare supplier email
- Build export package

**No fake-data policy:** external/live actions require real connectors or API keys. Missing connectors are reported instead of simulated.
