# Human review guide

The review queue is a decision gate. Screenshot extraction, automated-assistant
responses, and Labcoach-looking messages are candidates only; none are approved
by this pipeline.

## Allowed decisions

- `approved`: safe to copy into `data/approved/course-knowledge.json`.
- `rejected`: incorrect, irrelevant, unsafe, stale, or unsupported.
- `needs_clarification`: potentially useful but requires a clearer answer,
  conflict resolution, or a stronger source.

## Approval checklist

A row may be `approved` only when all conditions are true:

1. The answer comes from a verifiable Labcoach/announcement, or the team has
   checked it against an official source.
2. `corrected_answer` is accurate, concise, and contains no PII.
3. `official_source` identifies the document/channel/announcement used for
   verification without copying private identifiers.
4. Conflicts are resolved.
5. Volatile deadlines, schedules, locations, links, commands, and policies are
   still current and receive an expiry date when copied to the approved store.
6. `reviewer` and `reviewed_at` are completed.

Do not approve a learner-only claim or an automated assistant reply solely
because it appears confident. Do not copy screenshot usernames, Discord IDs,
avatar names, email addresses, phone numbers, or original filenames.

## Workflow

1. Start from the top of `review-queue.csv`; it is ordered by frequency,
   higher-authority candidate, logistics risk, unanswered status, and conflict.
2. Compare `source_image_ids` against local raw evidence.
3. Fill exactly one decision value.
4. For `approved`, fill `corrected_answer`, `official_source`, `reviewer`, and
   `reviewed_at`.
5. Copy only approved rows into `data/approved/course-knowledge.json`, set
   `status` to `approved`, and set `verified_by`/`verified_at`.
6. Run unit tests before demo.

The draft JSON must never be renamed or passed directly to runtime.

For the reviewed queue, promotion is performed by validation script rather than
manual JSON copying:

```powershell
python codebase/promote_knowledge.py
```

The script requires reviewer metadata and a current `valid_until` for every
approved volatile entry. It rejects PII, credentials, Wi-Fi passwords, original
filenames, duplicate questions, missing source IDs, and expired approved rows.
