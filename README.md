# CurveYield Security Audit Releases

This repository retains public CurveYield security audit PDF releases and their selected, sanitized supporting artifacts. Existing published Boosthub Staking v2 PDF and evidence remain unchanged.

The former Boosthub-only automatic PDF build workflow has been retired as part of the Audit-Controller reporting-generator v1 cutover. New releases use the selected-only immutable publisher in `curveyield3/Audit-Controller/audit-generator/src/report_v1/` when explicitly invoked for an accepted campaign with frozen publication consent.

Post-Phase-10 cross-repository dispatch is not yet enabled; this repository does not currently generate new reports automatically. The exact admitted source ZIP is published only if its initialization-time policy selected that role and its original archive bytes are verified; generated reconstructions are prohibited.
