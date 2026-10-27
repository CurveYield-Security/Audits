# CurveYield Security Audit Releases

This repository stores selected, sanitized public CurveYield audit PDFs and their supporting evidence. Existing published Boosthub Staking v2 release files are preserved.

The former Boosthub-specific automatic publisher is retired. For newly initialized Lite-Solo campaigns, all ten independently selectable publication roles default **ON**; withholding a role is an optional explicit choice made at initialization. Each selected original source ZIP must match the admitted archive bytes and pass the release safety checks. No ZIP is reconstructed and no private controller URLs, credentials, or unselected files are published.

The active publishing entrypoint is the accepted Phase-10 controller workflow in `curveyield3/Contract-Automation`, using its `CURVEYIELD_SECURITY_OWNER` secret to call GitHub's authenticated REST API. The canonical generator remains in private `curveyield3/Audit-Controller/audit-generator/src/report_v1/`. Every successfully generated final report also gets a private copy in its campaign `reports/delivery/<reportReleaseId>/report.pdf`; the public PDF is created only if `report_pdf` was selected.

Historical campaigns without a frozen initialization policy do not acquire retroactive public publication authorization. The public repository contains only immutable, selected-only release folders.
