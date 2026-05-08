# Certificate Inventory Integration

The uploaded certificate CSV has been integrated into the build as:

- `data/certificates.csv`
- `docs/CERTIFICATE_CSV_ANALYSIS.json`

## Detected CSV structure

```json
{
  "exists": true,
  "row_count": 1,
  "headers": [
    "Team",
    "Order Ref",
    "Order Label",
    "Duration",
    "Certificate Order Status",
    "Signed Certificate",
    "Signed Certificate Status",
    "Effective Date",
    "Expiration Date",
    "Common Name",
    "Organization Name",
    "Locality",
    "State",
    "Country",
    "SANs",
    "Order Date",
    "Certificate Serial Number",
    "Certificate Request Date",
    "Additional Email"
  ],
  "sample_rows": [
    {
      "Team": " ab3-1k5q8fk",
      "Order Ref": "co-f21k8gcsfc0",
      "Order Label": "Premium Multi-subdomain SSL",
      "Duration": "730",
      "Certificate Order Status": "waiting for csr",
      "Signed Certificate": "",
      "Signed Certificate Status": "",
      "Effective Date": "",
      "Expiration Date": "",
      "Common Name": "",
      "Organization Name": "",
      "Locality": "",
      "State": "",
      "Country": "",
      "SANs": "",
      "Order Date": "2025-07-28 21:35:59 -0500",
      "Certificate Serial Number": "",
      "Certificate Request Date": "[]",
      "Additional Email": "[]"
    }
  ]
}
```

## New modules

- `python/ai_serviter/certificate_manager.py`
- `python/ai_serviter/certificate_store.py`

## CLI usage

Generate report:

```bash
serviter . cert-report data/certificates.csv --warn-days 30
```

Import into SQLite store:

```bash
serviter . cert-import data/certificates.csv
```

Search:

```bash
serviter . cert-search data/certificates.csv example.com
```

Live TLS check:

```bash
serviter . cert-live-check example.com --port 443
```

## API endpoints

- `GET /certificates/latest`
- `POST /certificates/import` with JSON: `{"csv_path": "data/certificates.csv"}`
