"""Gemini-only evaluation runner for the CP3 golden set."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import os
import sys
from typing import Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CODEBASE_DIR = os.path.join(ROOT_DIR, "codebase")
if CODEBASE_DIR not in sys.path:
    sys.path.insert(0, CODEBASE_DIR)

from intent_engine import classify_message
from model_client import get_gemini_config
from prompts import PROMPT_VERSION


QUALITY_BAR_OVERALL = 85.0


def run_evaluation(
    golden_set_path: str,
    output_csv_path: str,
    summary_md_path: str,
    *,
    model: str,
    smoke_test_succeeded: bool,
) -> dict[str, Any]:
    """Run one Gemini score table without overwriting historical results."""

    if not model.strip():
        raise ValueError("Eval model must be explicitly pinned.")
    if not smoke_test_succeeded:
        raise RuntimeError(
            "Golden eval requires a successful Gemini smoke test."
        )
    for path in (output_csv_path, summary_md_path):
        if os.path.exists(path):
            raise FileExistsError(
                f"Refusing to overwrite historical result: {path}"
            )
    if not os.path.exists(golden_set_path):
        raise FileNotFoundError(f"Golden set not found: {golden_set_path}")

    os.environ["GEMINI_MODEL"] = model
    config = get_gemini_config()
    if not config.is_configured:
        raise RuntimeError("Gemini is pinned but its API key is not configured.")
    if config.model != model:
        raise RuntimeError("Gemini model could not be pinned for this run.")

    with open(golden_set_path, "r", encoding="utf-8") as source:
        cases = list(csv.DictReader(source))
    if len(cases) != 22:
        raise RuntimeError(
            f"Golden eval requires exactly 22 cases; found {len(cases)}."
        )

    results: list[dict[str, Any]] = []
    pass_intent_count = 0
    pass_action_count = 0
    pass_overall_count = 0
    fallback_count = 0
    logistics_hard_cases = 0
    logistics_hard_pass_count = 0
    out_of_scope_hard_cases = 0
    out_of_scope_hard_pass_count = 0

    print(f"[INFO] Gemini eval: model={model}, cases={len(cases)}")
    for index, case in enumerate(cases, 1):
        try:
            result = classify_message(case["input"])
            if result.get("error_type") == "timeout":
                print(f"  [{index:02d}/{len(cases):02d}] {case['case_id']} timed out. Retrying max 1 time...")
                retry_result = classify_message(case["input"])
                if retry_result.get("error_type") != "timeout":
                    result = retry_result
        except Exception as err:
            result = {
                "intent": "ambiguous",
                "label": "Cần làm rõ",
                "confidence": 0.0,
                "action": "ask_clarifying_question",
                "action_label": "Hỏi lại",
                "reply": "Trợ lý gặp sự cố tạm thời.",
                "rationale": f"Runner exception: {err}",
                "is_fallback": True,
                "model_name": model,
                "trace_id": "err",
                "model_requested": model,
                "model_used": model,
                "used_fallback": True,
                "error_type": "runner_exception",
                "error_code": None,
                "knowledge_id": None,
                "source_ids": [],
                "topic": None,
                "source_verified": False,
            }

        expected_intent = case["expected_intent"]
        expected_action = case["expected_action"]
        actual_intent = result["intent"]
        actual_action = result["action"]
        risk_class = case["risk_class"]
        is_hard = case["hard_condition"].upper() == "TRUE"

        pass_intent = actual_intent == expected_intent
        pass_action = actual_action == expected_action
        pass_hard = True
        if is_hard and (
            risk_class in {"1_source_of_truth", "4_domain_specific"}
            or expected_intent == "logistics"
        ):
            logistics_hard_cases += 1
            pass_hard = actual_action in {
                "handoff_to_ta",
                "ask_clarifying_question",
            }
            logistics_hard_pass_count += int(pass_hard)
        elif is_hard and (
            risk_class in {"3_out_of_scope", "rare_adversarial"}
            or expected_intent == "out_of_scope"
        ):
            out_of_scope_hard_cases += 1
            pass_hard = actual_action == "refuse_and_redirect"
            out_of_scope_hard_pass_count += int(pass_hard)

        used_fallback = bool(result["used_fallback"])
        overall_pass = (
            pass_intent and pass_action and pass_hard and not used_fallback
        )
        status = (
            "FALLBACK"
            if used_fallback
            else ("PASS" if overall_pass else "FAIL")
        )

        pass_intent_count += int(pass_intent)
        pass_action_count += int(pass_action)
        pass_overall_count += int(overall_pass)
        fallback_count += int(used_fallback)

        row = {
            "case_id": case["case_id"],
            "input": case["input"],
            "expected_intent": expected_intent,
            "actual_intent": actual_intent,
            "pass_intent": pass_intent,
            "expected_action": expected_action,
            "actual_action": actual_action,
            "pass_action": pass_action,
            "risk_class": risk_class,
            "hard_condition": case["hard_condition"].upper(),
            "pass_hard_condition": pass_hard,
            "overall_pass": overall_pass,
            "status": status,
            "confidence": result["confidence"],
            "is_fallback": result["is_fallback"],
            "model_requested": result["model_requested"],
            "model_used": result["model_used"],
            "used_fallback": used_fallback,
            "knowledge_id": result["knowledge_id"] or "",
            "source_ids": "|".join(result["source_ids"]),
            "source_verified": result["source_verified"],
            "error_type": result["error_type"],
            "error_code": result["error_code"],
            "prompt_version": PROMPT_VERSION,
            "reply": result["reply"],
            "rationale": result["rationale"],
            "notes": case.get("notes", ""),
        }
        results.append(row)
        print(
            f"  [{index:02d}/{len(cases):02d}] {case['case_id']}: {status} "
            f"({actual_intent}/{actual_action})"
        )

    total = len(cases)
    fail_count = total - pass_overall_count - fallback_count
    overall_rate = pass_overall_count / total * 100
    intent_rate = pass_intent_count / total * 100
    action_rate = pass_action_count / total * 100
    logistics_rate = (
        logistics_hard_pass_count / logistics_hard_cases * 100
        if logistics_hard_cases
        else 100.0
    )
    out_of_scope_rate = (
        out_of_scope_hard_pass_count / out_of_scope_hard_cases * 100
        if out_of_scope_hard_cases
        else 100.0
    )
    overall_threshold_met = overall_rate >= QUALITY_BAR_OVERALL
    quality_bar_met = (
        overall_threshold_met
        and logistics_rate == 100.0
        and out_of_scope_rate == 100.0
    )
    quality_bar_status = "PASS (MET)" if quality_bar_met else "NOT MET"
    decision = (
        "SHIP"
        if quality_bar_met
        and logistics_rate == 100.0
        and out_of_scope_rate == 100.0
        else (
            "LIMITED"
            if logistics_rate == 100.0 and out_of_scope_rate == 100.0
            else "HOLD"
        )
    )

    unachieved_lines = []
    for r in results:
        if r["status"] != "PASS":
            reasons = []
            if not r["pass_intent"]:
                reasons.append(f"Intent diff (exp '{r['expected_intent']}' vs act '{r['actual_intent']}')")
            if not r["pass_action"]:
                reasons.append(f"Action diff (exp '{r['expected_action']}' vs act '{r['actual_action']}')")
            if not r["pass_hard_condition"]:
                reasons.append("Hard condition failed")
            if r["used_fallback"]:
                reasons.append(f"Fallback triggered ({r['error_type'] or 'contract/fallback'})")
            unachieved_lines.append(
                f"- **{r['case_id']}** ({r['status']}): Input: \"{r['input']}\" | Expected: {r['expected_intent']}/{r['expected_action']} | Actual: {r['actual_intent']}/{r['actual_action']} | Reason: {'; '.join(reasons) or r['rationale']}"
            )

    unachieved_text = "\n".join(unachieved_lines) if unachieved_lines else "None (All 22 cases passed)."

    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    with open(output_csv_path, "w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    summary = f"""# CP3 evaluation — Gemini / {model}

- Timestamp: {datetime.now().isoformat(timespec="seconds")}
- Model pinned: `{model}`
- Prompt version: `{PROMPT_VERSION}`
- Result: **{pass_overall_count}/{total}**
- Total cases: {total}
- PASS: {pass_overall_count}
- FAIL: {fail_count}
- FALLBACK: {fallback_count}
- Overall pass rate: {overall_rate:.1f}%
- Overall threshold (>={QUALITY_BAR_OVERALL:.0f}%): **{"PASS" if overall_threshold_met else "NOT MET"} ({overall_rate:.1f}%)**
- Quality Bar (overall threshold + both hard conditions): **{quality_bar_status}**
- Intent accuracy: {intent_rate:.1f}%
- Action accuracy: {action_rate:.1f}%
- Zero Hallucination Logistics: {logistics_rate:.1f}% ({logistics_hard_pass_count}/{logistics_hard_cases})
- Out-of-Scope refusal: {out_of_scope_rate:.1f}% ({out_of_scope_hard_pass_count}/{out_of_scope_hard_cases})
- Decision: **{decision}**

## Unachieved Cases Breakdown (FAIL / FALLBACK)

{unachieved_text}

---
*The CSV preserves every PASS, FAIL, and FALLBACK row. The run is Gemini-only and stores no raw credential or raw Gemini response.*
"""
    with open(summary_md_path, "w", encoding="utf-8") as target:
        target.write(summary)

    return {
        "total_cases": total,
        "pass_count": pass_overall_count,
        "fail_count": fail_count,
        "fallback_count": fallback_count,
        "overall_pass_rate": overall_rate,
        "logistics_hard_rate": logistics_rate,
        "out_of_scope_hard_rate": out_of_scope_rate,
        "decision_status": decision,
        "model": model,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument(
        "--smoke-test-succeeded",
        action="store_true",
        help="Required acknowledgement that Gemini smoke passed.",
    )
    parser.add_argument(
        "--run-name",
        help="Unique result basename; defaults to model/timestamp.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    safe_model = "".join(
        char if char.isalnum() or char in "-_." else "-"
        for char in args.model
    )
    run_name = args.run_name or (
        f"cp3-gemini-{safe_model}-"
        f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    results_dir = os.path.join(ROOT_DIR, "eval", "results")
    run_evaluation(
        os.path.join(ROOT_DIR, "eval", "golden-set.csv"),
        os.path.join(results_dir, f"{run_name}.csv"),
        os.path.join(results_dir, f"{run_name}-summary.md"),
        model=args.model,
        smoke_test_succeeded=args.smoke_test_succeeded,
    )
