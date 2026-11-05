# Changelog

All notable changes to the Coupa Integration Baseline (CIB) will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-11-05

CIB has no update or upgrade path between versions. A deployed CIB becomes
an independent fork, so 2.1.0 is for new deployments; existing 2.0.x
deployments are not upgraded.

### Added
- **Italy.** `6. Italy` workspace with an `AP Documents - IT` queue on the
  shared line-level engine, and a `Move to IT queue` rule on the E-invoicing
  Inbox. `Coupa E-Invoicing` gains a `FatturaElettronica` (FatturaPA) mapping
  that sets `source_country` to `IT`; `TD04` / `TD08` map to credit notes.
- **Mexico.** `7. Mexico` workspace with an `AP Documents - MX` queue on the
  shared line-level engine, and a `Move to MX queue` rule on the E-invoicing
  Inbox. `Coupa E-Invoicing` gains a CFDI 4.0 `Comprobante` mapping
  (`TipoDeComprobante` `I` or `E`) that sets `source_country` to `MX`.
  - New `cfdi_section` on the MX queue and the Inbox: `series`, `folio_number`,
    `use_of_invoice`, `form_of_payment`, `payment_method`, `issuance_place`,
    `confirmation`, `type_of_relationship`.
  - `Export Mapping - Line Level Taxation` sends these as `series`,
    `folio-number`, `use-of-invoice`, `form-of-payment`, `payment-method`,
    `issuance-place`, `confirmation` and `type-of-relationship` when they are
    set.
- `item_po_line_number` line-item field on every queue, an engine field on
  both extraction engines, and mapped from the e-invoice XML.
- Nine new engine fields on `AP Documents - line level taxation` (the CFDI
  fields above plus `item_po_line_number`) and one on
  `AP Documents - header level taxation` (`item_po_line_number`).
- The IT and MX queues are attached to the same baseline hooks and business
  rules as the other country queues. `Get Barcodes - KSeF PL` stays on the
  PL queue only.

### Changed
- `Coupa E-Invoicing`: UBL and CII selectors for `Invoice` and `CreditNote`
  are merged into single expressions. Seller/buyer tax and party IDs, the
  currency code and the credit-note reason now resolve with an explicit
  fallback order.
- `Coupa E-Invoicing`: the currency code is now lowercased directly from the
  XML instead of going through a fixed 16-currency mapping table, so a
  currency outside that table is no longer mapped to `other`.
- E-invoicing Inbox schema: `source_country` is now required. `currency`,
  `charge_amount` and `charge_type` are no longer required on the Inbox.
- `deploy/cib_target.yaml` regenerated to include the new workspaces, queues,
  schemas, inboxes, rules and engine fields. `cib_target_secrets.json`,
  `hooks.csv` and `required_scopes.json` are unchanged, so no new secrets,
  service URLs or Coupa OAuth scopes are needed.

---

## [2.0.1] - 2026-09-24

### Fixed
- `Coupa E-Invoicing`: the `UN/CEFACT CII - France` mapping now triggers only
  when the buyer's `CountryID` is `FR`. Previously it matched any CII invoice.
- `deploy/required_scopes.json` was not valid JSON in 2.0.0, so the CIB init
  script skipped the Coupa credential scope check. Restored.

---

## [2.0.0] - 2026-09-24

Major release. CIB 2.0 is a **fresh install only** — there is no in-place upgrade
path from 1.x. Deploy it into a clean organisation.

### Added
- **E-invoicing.** An `E-invoicing Inbox` queue that parses inbound e-invoice XML
  (KSeF, UBL, CII, ZUGFeRD/X-Rechnung, Factur-X) via the `Coupa E-Invoicing` hook
  and routes each document to a country queue.
- **Country AP queues** for Belgium, Poland, France and Germany, sharing the
  baseline schema plus the fields their market requires.
- `Coupa E-Invoicing Status Sync` and `… - Inbox` hooks, reporting Rossum
  annotation status back to Coupa's `invoice_enrichable_documents` endpoint.
- `Get Barcodes - KSeF PL` hook for Polish KSeF barcode retrieval.
- 21 fields on the line-level baseline queue that previously existed only on the
  country queues, so the shared line-level export mapping resolves everywhere.
  Twenty are captured with `score_threshold: 0.0` and no pretrained seed;
  `type_of_receipt` is a `data` field written from the e-invoice XML.
- `deploy/` — the deploy file, secrets template, `hooks.csv` and
  `required_scopes.json` that the CIB init script consumes. Previously these
  lived in the init-script repository and had to be kept in sync by hand.
  They are generated from this release's `cib-org/` tree, so they always match it.

### Changed
- **Export rewritten onto the Request Processor.** The eight REST-API-export and
  data-value-extractor webhooks (`Create Draft`, `Attach Image Scan`,
  `Attach Rossum URL`, `Submit document` and their four `- parse response`
  partners) are replaced by five serverless `Export Pipeline - N.` functions
  chained with `run_after`. They carry no per-cluster URL, so a deployment no
  longer has to point them at the right region.
  - New stage: `Export Pipeline - 4. Attach Supplementary Files`.
  - API responses now land in `document_relations` instead of schema fields;
    `Handle Coupa Responses` reads them from there and gates the submit step on
    `sf_submit_for_approval`.
- **Extraction engines rebuilt** as `AP Documents - line level taxation` (63
  fields, serving the baseline line queue, the inbox and the four country
  queues) and `AP Documents - header level taxation` (41 fields). All Coupa
  pretrained field bindings carry over from 1.x unchanged.
- Schema reorganised: `coupa_technical_fields` is split into `Export Pipeline`,
  `Submission Control`, `Validation & Tags` and `Header Queue Compatibility`.
- Business rule names no longer carry the `TEST - ` prefix.
- `MDH - Coupa Invoice Check` takes its Coupa URLs as literals rather than from
  the removed `oauth_url` / `create_draft_url` schema fields. The init script
  rewrites both at deploy time.
- `contract_number_normalized` no longer strips non-alphanumeric characters. The
  MDH contract lookup matches Coupa's `number` exactly, so stripping broke any
  contract number containing a separator.

### Removed
- 13 export-plumbing schema fields superseded by the Request Processor:
  `api1_status`, `api{1,2,3,4}_response_body`, `api{2,3,4}_url`,
  `api{2,4}_gate`, `oauth_url`, `create_draft_url`.

### Unchanged from 1.1.0
All 48 baseline business rules keep their trigger conditions and actions
byte-for-byte, every shared schema formula is identical, and `MDH - Main` and
`MDH - Tax Codes` — which carry the PO, supplier and customer matching cascades
— are unchanged.

---

## [1.1.0] - 2026-06-19

### Changed
- Import hooks: changed sorting from `created_at` to `id` for more reliable ordering on bulk-imported data (applies to all 12 Coupa Webhook Import hooks)

---

## [1.0.0] - 2026-06-17

### Added
- Initial public release of the Coupa Integration Baseline (CIB)
