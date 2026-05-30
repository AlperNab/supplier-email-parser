# supplier-email-parser

> **Supplier email thread → structured purchase order data.** Items, quantities, prices, delivery dates, payment terms, discrepancies flagged, PO draft auto-generated.

[![PyPI](https://img.shields.io/pypi/v/supplier-email-parser?style=flat)](https://pypi.org/project/supplier-email-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quickstart

```bash
pip install supplier-email-parser
python -m supplier_email_parser email_thread.txt
python -m supplier_email_parser email.txt --json
```

## What it extracts

- **Line items** — description, quantity, unit, unit price, total per line
- **Supplier details** — company, country, payment terms, lead time
- **Delivery** — requested and confirmed dates, incoterms, destination
- **Payment** — terms, deposit %, balance trigger
- **Action items** — what needs to happen next, by whom, by when
- **Discrepancies** — price changes, quantity mismatches, missing info
- **PO readiness** — whether a PO can be issued or what's blocking it

## License
MIT © [Alper Nabil Gabra Zakher](https://github.com/AlperNab)
