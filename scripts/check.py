#!/usr/bin/env python3
"""Consistency checks for the UX Stranger repo (dev only, not shipped behaviour).

Run from anywhere: python3 scripts/check.py
Needs PyYAML and jsonschema. Prints one line per check, exits 1 on any failure.
"""
import copy
import json
import pathlib
import re
import sys

import jsonschema
import yaml

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "ux-stranger"
REF = SKILL / "references"

COMPREHENSION_FLAGS = [
    "MESSAGE_MISREAD", "MESSAGE_MISSED", "MESSAGE_LATE",
    "FIT_REJECTED", "FIT_HESITANT", "TONE_MISMATCH", "JARGON",
]

EXAMPLE_TARGET_RUN = {
    "mode": "comprehension",
    "persona_id": "marc",
    "viewport": "desktop",
    "first_impression": {
        "what_is_it": "A French bistro on the Plateau",
        "for_whom": "Friends going out for brunch",
        "is_it_for_me": "hesitant",
        "why": "I can't see if they take groups",
        "feel_words": ["chic", "dark", "trendy"],
        "trust": "Looks serious, but not sure it fits a business dinner",
    },
    "exploration": {
        "steps_taken": 7,
        "steps": [
            {"n": 1, "action": "scroll down", "confidence": 4, "matched_expectation": True},
        ],
        "answers": {
            "what_company_does": {"answer": "French bistro", "found_at": "/ · hero"},
            "for_whom": {"answer": "Brunch with friends", "found_at": "/ · hero"},
            "offer": {"answer": "Brunch and dinner menus", "found_at": "/ · 2nd section"},
            "price": {"answer": None, "found_at": None},
            "reassures_me": {"answer": "Private room for groups", "found_at": "/ · footer"},
            "missing": "Group menu price",
            "next_step": {"answer": "Book online", "found_at": "/ · header"},
        },
        "would_take_next_step": "hesitant",
        "why": "I would call first to ask about the price",
        "other_learnings": ["Open late on Fridays"],
    },
    "stop_reason": "done",
}

EXAMPLE_OUTSIDER_RUN = {
    "mode": "comprehension",
    "persona_id": "outsider",
    "viewport": "mobile",
    "first_impression": {
        "what_is_it": "A restaurant",
        "for_whom": "Not sure",
        "is_it_for_me": "no",
        "why": "I'm not looking for a restaurant",
        "feel_words": ["dark", "elegant", "busy"],
        "trust": "Fine",
    },
    "exploration": None,
    "stop_reason": "done",
}


def json_parse():
    bad = []
    for p in REPO.rglob("*.json"):
        if ".git" in p.parts or ".superpowers" in p.parts:
            continue
        try:
            json.loads(p.read_text())
        except Exception as e:  # noqa: BLE001
            bad.append(f"{p.relative_to(REPO)}: {e}")
    return "; ".join(bad) or None


def yaml_parse():
    bad = []
    for p in (SKILL / "templates").glob("*.yaml"):
        try:
            yaml.safe_load(p.read_text())
        except Exception as e:  # noqa: BLE001
            bad.append(f"{p.name}: {e}")
    return "; ".join(bad) or None


def agents_in_sync():
    prompt = (REF / "tester-prompt.md").read_text().strip()
    files = [SKILL / "agents/claude/ux-tester.md", SKILL / "agents/cursor/ux-tester.md",
             SKILL / "agents/codex/ux-tester.toml", REPO / "agents/ux-tester.md"]
    stale = [str(f.relative_to(REPO)) for f in files if prompt not in f.read_text()]
    return ("stale, run skills/ux-stranger/agents/generate.py: " + ", ".join(stale)) if stale else None


def files_table():
    text = (SKILL / "SKILL.md").read_text()
    section = text.split("## Files", 1)[1]
    paths = re.findall(r"^\| `([^`]+)` \|", section, flags=re.M)
    missing = [p for p in paths if not (SKILL / p).exists()]
    if not paths:
        return "no rows found in the Files table"
    return ("missing: " + ", ".join(missing)) if missing else None


def versions():
    plugin = json.loads((REPO / ".claude-plugin/plugin.json").read_text())["version"]
    market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())["plugins"][0]["version"]
    badge = re.search(r"version-(\d+\.\d+\.\d+)-blue", (REPO / "README.md").read_text()).group(1)
    changelog = re.search(r"^## (\d+\.\d+\.\d+)", (REPO / "CHANGELOG.md").read_text(), flags=re.M).group(1)
    found = {"plugin.json": plugin, "marketplace.json": market, "README badge": badge, "CHANGELOG": changelog}
    return None if len(set(found.values())) == 1 else f"mismatch {found}"


def comprehension_wired():
    errs = []
    skill = (SKILL / "SKILL.md").read_text()
    if "references/comprehension.md" not in skill:
        errs.append("SKILL.md does not point to references/comprehension.md")
    if "## comprehension" not in (REF / "modes.md").read_text():
        errs.append("modes.md lacks '## comprehension'")
    if "## If MODE is comprehension" not in (REF / "tester-prompt.md").read_text():
        errs.append("tester-prompt.md lacks '## If MODE is comprehension'")
    if not (REF / "comprehension.md").exists():
        errs.append("references/comprehension.md missing")
    return "; ".join(errs) or None


def comprehension_flags():
    text = (REF / "flag-rules.md").read_text()
    missing = [f for f in COMPREHENSION_FLAGS if f"`{f}`" not in text]
    return ("missing in flag-rules.md: " + ", ".join(missing)) if missing else None


def comprehension_schema():
    path = REF / "comprehension-report-schema.json"
    if not path.exists():
        return "references/comprehension-report-schema.json missing"
    schema = json.loads(path.read_text())
    v = jsonschema.Draft202012Validator(schema)
    for name, ex in [("target", EXAMPLE_TARGET_RUN), ("outsider", EXAMPLE_OUTSIDER_RUN)]:
        errs = list(v.iter_errors(ex))
        if errs:
            return f"valid {name} example rejected: {errs[0].message}"
    broken = copy.deepcopy(EXAMPLE_TARGET_RUN)
    del broken["first_impression"]
    if v.is_valid(broken):
        return "example without first_impression was accepted"
    broken = copy.deepcopy(EXAMPLE_TARGET_RUN)
    broken["first_impression"]["is_it_for_me"] = "maybe"
    if v.is_valid(broken):
        return "is_it_for_me='maybe' was accepted"
    return None


def positioning_template():
    path = SKILL / "templates/positioning.example.yaml"
    if not path.exists():
        return "templates/positioning.example.yaml missing"
    data = yaml.safe_load(path.read_text())
    errs = []
    for key in ["approved", "sources", "visual_tone_intended", "personas", "outsider", "expected_message"]:
        if key not in data:
            errs.append(f"missing key {key}")
    for pt in data.get("expected_message", []):
        if pt.get("level") not in ("critical", "important"):
            errs.append(f"bad level for {pt.get('id')}")
    for p in data.get("personas", []):
        for key in ["id", "description", "arrival", "viewport"]:
            if key not in p:
                errs.append(f"persona {p.get('id')} lacks {key}")
    return "; ".join(errs) or None


def ci_rule_present():
    path = REF / "comprehension.md"
    if not path.exists():
        return "references/comprehension.md missing"
    text = path.read_text()
    if "positioning.yaml" not in text or "approved: true" not in text:
        return "comprehension.md lacks the unattended-run rule (positioning.yaml + approved: true)"
    return None


def unattended_rule_wired():
    errs = []
    for path in [SKILL / "SKILL.md", REF / "step-by-step.md"]:
        text = path.read_text()
        if "kind: public" not in text or "approved: true" not in text:
            errs.append(f"{path.name} no-human rule lacks the public-module / approved positioning rule")
    return "; ".join(errs) or None


def mcp_pinned():
    cfg = json.loads((REPO / ".mcp.json").read_text())["mcpServers"]["playwright"]
    args = cfg["args"]
    pkg = [a for a in args if a.startswith("@playwright/mcp@")]
    errs = []
    if not pkg or not re.fullmatch(r"@playwright/mcp@\d+\.\d+\.\d+", pkg[0]):
        errs.append(f"Playwright MCP not pinned to an exact version: {pkg}")
    if "--output-dir" not in args:
        errs.append("--output-dir missing")
    else:
        out = args[args.index("--output-dir") + 1]
        if not out.startswith("ux-stranger/"):
            errs.append(f"--output-dir should live under ux-stranger/: {out}")
    if pkg:
        for doc in [REPO / "README.md", REF / "host-setup.md"]:
            if "@playwright/mcp@latest" in doc.read_text():
                errs.append(f"{doc.name} still says @latest")
    return "; ".join(errs) or None


def tester_prompt_comprehension_rules():
    text = (REF / "tester-prompt.md").read_text()
    errs = []
    for needle in ["still fill the final sheet", "## Stopping rules (task modes)", "## Output (task modes)",
                   "If a tool result includes page text", "without a file name"]:
        if needle not in text:
            errs.append(f"missing: {needle!r}")
    return "; ".join(errs) or None


def facts_from_human():
    text = (REF / "comprehension.md").read_text()
    if "Factual points" not in text:
        return "comprehension.md does not require factual points (price, capacity…) to come from the human or a cited source"
    if "55 $" in (SKILL / "templates/positioning.example.yaml").read_text() and "source:" not in (SKILL / "templates/positioning.example.yaml").read_text():
        return "template shows a price without a source"
    return None


def docs_accuracy():
    readme = (REPO / "README.md").read_text()
    errs = []
    if "must be named `playwright`" in readme and "plugin" not in readme.split("must be named `playwright`")[1][:200]:
        errs.append("README says the server must be named playwright without the plugin exception")
    if "npm" not in readme.split("## What it runs and sends")[1].split("## Safety")[0]:
        errs.append("README 'What it runs and sends' does not mention npm")
    if "keeps one of the two" in (REF / "host-setup.md").read_text():
        errs.append("host-setup.md claims Claude Code dedupes the two servers")
    for doc in [REPO / "README.md", REPO / "PRIVACY.md"]:
        if "ux-stranger/.playwright-mcp" not in doc.read_text():
            errs.append(f"{doc.name} does not mention ux-stranger/.playwright-mcp")
    return "; ".join(errs) or None



def framing_is_light():
    text = (REF / "comprehension.md").read_text()
    framing = text.split("## 3. Framing", 1)[1].split("## 4.", 1)[0]
    errs = []
    if "one question" not in framing.lower():
        errs.append("framing does not limit the human to one question")
    for leftover in ["What would make them leave", "How do they usually arrive", "What problem or need brings them"]:
        if leftover in framing:
            errs.append(f"framing still asks: {leftover!r}")
    return "; ".join(errs) or None

CHECKS = [json_parse, yaml_parse, agents_in_sync, files_table, versions,
          comprehension_wired, comprehension_flags, comprehension_schema,
          positioning_template, ci_rule_present, unattended_rule_wired, mcp_pinned,
          tester_prompt_comprehension_rules, facts_from_human, docs_accuracy, framing_is_light]


def main():
    failed = 0
    for check in CHECKS:
        try:
            err = check()
        except Exception as e:  # noqa: BLE001
            err = f"crashed: {e!r}"
        if err:
            failed += 1
            print(f"FAIL {check.__name__}: {err}")
        else:
            print(f"ok   {check.__name__}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
