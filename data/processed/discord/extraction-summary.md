# Discord screenshot extraction summary

## Coverage

- Input screenshots: 65
- Successfully inspected: 65
- Fully unreadable screenshots: 0
- Extracted messages: 88
- Learner questions: 56
- Labcoach answer candidates: 5
- Unanswered FAQ candidates: 15
- Duplicate/near-duplicate question groups: 9
- FAQ candidates: 33
- Candidates with conflicts: 1
- Candidates containing volatile information: 30

## Redaction accounting

- Source identity headers excluded (username and/or Discord identifier): 65
- Avatar/display identity excluded: 65
- QR payload excluded: 1
- Course URL redacted from processed text: 1
- Email addresses or phone numbers copied into processed data: 0

The counts above describe exclusions from processed text; raw screenshots remain
local-only evidence and are ignored by Git.

## Image IDs needing focused human review

IMG-001, IMG-003, IMG-006, IMG-009, IMG-015, IMG-030, IMG-035, IMG-037, IMG-042, IMG-052, IMG-055, IMG-061, IMG-062, IMG-063, IMG-065

## Limitations

- OCR was performed by direct local visual inspection in seven batches because
  no local Tesseract/EasyOCR runtime was available.
- Confidence is an extraction estimate, not a calibrated OCR probability.
- Cropped screenshots can omit reply targets and surrounding context.
- Automated assistant replies are not treated as official course knowledge.
- Learner statements are never promoted to authority.
- Dates, schedules, links, locations, role rules, XP rules, and submission
  commands can become stale and therefore remain volatile.
- No candidate is described as official or Labcoach-verified until a human
  reviewer supplies an official source and approval.
