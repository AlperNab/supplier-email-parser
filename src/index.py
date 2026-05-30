#!/usr/bin/env python3
"""
supplier-email-parser — supplier email thread → structured purchase order data
Extracts: items, quantities, prices, delivery dates, payment terms,
supplier details, discrepancies, auto-generates PO draft
"""
import anthropic, json, re, sys
from pathlib import Path
from datetime import datetime, timezone

SYSTEM = """You are a procurement specialist and supply chain analyst.
Extract all purchase order data from this supplier email thread.

Rules:
- Extract ONLY what is explicitly stated — never infer quantities or prices
- Flag any discrepancies (price changes, quantity mismatches, missing info)
- Normalize units (pcs/pieces/units → units, kgs/kilograms → kg)
- Dates should be YYYY-MM-DD
- Prices in original currency, note currency clearly

Return ONLY valid JSON — no markdown, no explanation.

{
  "email_thread_summary": "2-3 sentences describing the negotiation/order status",
  "order_status": "inquiry|quote_received|negotiating|confirmed|amended|cancelled",
  "supplier": {
    "name": "string or null",
    "email": "string or null",
    "company": "string or null",
    "country": "string or null",
    "payment_terms": "NET30|COD|50/50|string or null",
    "lead_time_days": number_or_null
  },
  "buyer": {
    "name": "string or null",
    "email": "string or null",
    "company": "string or null"
  },
  "line_items": [
    {
      "item_number": number,
      "sku": "string or null",
      "description": "product description",
      "quantity": number,
      "unit": "units|kg|liters|boxes|pallets|...",
      "unit_price": number_or_null,
      "currency": "USD|EUR|CNY|EGP|...",
      "total_price": number_or_null,
      "moq": number_or_null,
      "lead_time_days": number_or_null,
      "notes": "string or null"
    }
  ],
  "totals": {
    "subtotal": number_or_null,
    "shipping": number_or_null,
    "tax": number_or_null,
    "total": number_or_null,
    "currency": "string"
  },
  "delivery": {
    "requested_date": "YYYY-MM-DD or null",
    "confirmed_date": "YYYY-MM-DD or null",
    "shipping_method": "string or null",
    "incoterms": "FOB|CIF|DDP|EXW|string or null",
    "destination": "string or null"
  },
  "payment": {
    "terms": "string or null",
    "deposit_pct": number_or_null,
    "balance_trigger": "string or null",
    "bank_details_provided": true_or_false
  },
  "attachments_mentioned": ["list of mentioned attachments"],
  "action_items": [
    {
      "action": "what needs to happen next",
      "owner": "buyer|supplier|both",
      "deadline": "YYYY-MM-DD or null",
      "priority": "urgent|normal|low"
    }
  ],
  "discrepancies": [
    {
      "issue": "description of the discrepancy",
      "field": "price|quantity|date|terms|other",
      "expected": "string",
      "actual": "string"
    }
  ],
  "po_draft": {
    "po_number": "PO-{YYYYMMDD}-001",
    "ready_to_issue": true_or_false,
    "blocking_issues": ["list of things preventing PO issuance"],
    "suggested_po_lines": "condensed PO summary"
  },
  "confidence": 0.0
}"""

def parse(email_text: str) -> dict:
    client = anthropic.Anthropic()
    if len(email_text) > 30000:
        email_text = email_text[:30000]
    resp = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=3000, system=SYSTEM,
        messages=[{"role":"user","content":f"Extract purchase order data from this email thread:\n\n{email_text}"}]
    )
    raw = re.sub(r'^```(?:json)?\s*','',resp.content[0].text.strip(),flags=re.MULTILINE)
    raw = re.sub(r'\s*```$','',raw,flags=re.MULTILINE)
    return json.loads(raw)

def parse_file(path: str) -> dict:
    return parse(Path(path).read_text(encoding="utf-8",errors="replace"))

STATUS_ICON = {"inquiry":"📩","quote_received":"📋","negotiating":"🤝","confirmed":"✅","amended":"✏️","cancelled":"❌"}

def print_report(r: dict):
    sup = r.get("supplier",{})
    delivery = r.get("delivery",{})
    payment = r.get("payment",{})
    totals = r.get("totals",{})
    po = r.get("po_draft",{})
    status = r.get("order_status","inquiry")

    print(f"\n{'═'*60}")
    print(f"  SUPPLIER EMAIL PARSER")
    print(f"  Status: {STATUS_ICON.get(status,'')} {status.upper().replace('_',' ')}")
    print(f"{'═'*60}")
    print(f"\n  {r.get('email_thread_summary','')}")

    print(f"\n  Supplier: {sup.get('company','?')} ({sup.get('country','?')})")
    if sup.get("payment_terms"): print(f"  Payment:  {sup['payment_terms']}")
    if sup.get("lead_time_days"): print(f"  Lead time:{sup['lead_time_days']} days")

    items = r.get("line_items",[])
    if items:
        curr = totals.get("currency","")
        print(f"\n  LINE ITEMS ({len(items)})")
        for item in items:
            price = f"  {item.get('currency','')}{item.get('unit_price',0):.2f}/{item.get('unit','unit')}" if item.get("unit_price") else ""
            total = f"  = {item.get('currency','')}{item.get('total_price',0):.2f}" if item.get("total_price") else ""
            print(f"  [{item.get('item_number','?')}] {item.get('description','?')}")
            print(f"      Qty: {item.get('quantity',0)} {item.get('unit','')}{price}{total}")

    if totals.get("total"):
        print(f"\n  TOTAL: {totals.get('currency','')}{totals['total']:,.2f}")
        if totals.get("shipping"): print(f"  Shipping: {totals.get('currency','')}{totals['shipping']:,.2f}")

    if delivery.get("confirmed_date") or delivery.get("requested_date"):
        print(f"\n  Delivery: {delivery.get('confirmed_date') or delivery.get('requested_date','?')}")
        if delivery.get("incoterms"): print(f"  Incoterms: {delivery['incoterms']}")

    discrepancies = r.get("discrepancies",[])
    if discrepancies:
        print(f"\n  ⚠ DISCREPANCIES ({len(discrepancies)})")
        for d in discrepancies:
            print(f"  ! {d.get('issue','')}")
            print(f"    Expected: {d.get('expected','')} | Actual: {d.get('actual','')}")

    actions = r.get("action_items",[])
    if actions:
        print(f"\n  ACTION ITEMS")
        for a in actions:
            deadline = f" by {a['deadline']}" if a.get("deadline") else ""
            print(f"  → [{a.get('owner','?').upper()}] {a.get('action','')}{deadline}")

    print(f"\n  PO Ready: {'✅ YES' if po.get('ready_to_issue') else '❌ NO'}")
    for issue in po.get("blocking_issues",[]): print(f"  ! {issue}")
    print(f"  Confidence: {int(r.get('confidence',0)*100)}%")
    print(f"{'═'*60}\n")

if __name__ == "__main__":
    if len(sys.argv)<2: print("Usage: python -m supplier_email_parser <email.txt> [--json]"); sys.exit(0)
    src = sys.argv[1]
    r = parse_file(src) if Path(src).exists() else parse(sys.stdin.read() if src=="-" else src)
    if "--json" in sys.argv: print(json.dumps(r,indent=2,ensure_ascii=False))
    else: print_report(r)
