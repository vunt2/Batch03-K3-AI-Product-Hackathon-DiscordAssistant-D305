# Discord knowledge data

This directory separates raw evidence, review artifacts, and runtime-approved
knowledge.

- `raw/discord-screenshots/`: source screenshots and the local filename mapping
  were removed after extraction and review. Git ignores this path if raw files
  are collected again because filenames and images may contain PII.
- `processed/discord/`: anonymized OCR output, FAQ candidates, review queue,
  draft knowledge, and extraction quality notes. Nothing here is approved by
  default.
- `approved/course-knowledge.json`: the only knowledge file that runtime may
  load. Human reviewers copy approved, verified, non-conflicting entries here.

The screenshots are used to create retrieval context only. They are not
fine-tuning or model-training data.

## Audited counts (2026-07-30)

- 65 raw screenshot image files were processed and then removed locally; they
  are not part of the submission repository.
- Processed extraction contains 88 anonymized message records and 33 FAQ
  candidates.
- A claim of “100 Discord messages” is **UNVERIFIED** and must not be used as
  project evidence unless a traceable dataset supports it.
- Human review/promotion currently yields 27 approved runtime entries, 2
  expired records and 4 needs-clarification/handoff records.
