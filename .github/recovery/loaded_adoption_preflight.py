#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.request
from typing import Any

REPAIR = "human-cascade-live-20260817T2058CT-7B3F91D2"
REVENUE = "everything-revenue-front-1dade875-d140-4eb7-92b2-0e3651e694be"


def run(argv: list[str], timeout: float = 12.0) -> dict[str, Any]:
    try:
        proc = subprocess.run(argv, text=True, capture_output=True, timeout=timeout, check=False)
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout[-12000:],
            "stderr": proc.stderr[-2000:],
        }
    except Exception as exc:
        return {"exception": f"{type(exc).__name__}: {exc}"}


def sha(path: str) -> str:
    try:
        return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    except Exception:
        return ""


def emit(name: str, value: Any) -> None:
    print(f"{name}=" + json.dumps(value, sort_keys=True, default=str), flush=True)


def compact_activation(persona: str) -> dict[str, Any]:
    path = pathlib.Path(
        "/home/evan/.local/share/live/worlds/v1/cognilode/universe/employee_runtime/activation_requests"
    ) / f"employee_{persona}.json"
    try:
        value = json.loads(path.read_text()) if path.exists() else {}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    keys = (
        "request_id",
        "correlation_id",
        "semantic_sender",
        "source_created_at_s",
        "state",
        "attempts",
        "submission_observed",
        "response_started",
        "transport_status",
        "transport_attempt_state",
        "last_error",
        "next_attempt_at_s",
    )
    return {key: value.get(key) for key in keys}


def main() -> int:
    emit(
        "META",
        {
            "schema": "everything.prekickoff.loaded_adoption_preflight.v2",
            "observed_at_s": time.time(),
            "repair_correlation": REPAIR,
            "revenue_correlation": REVENUE,
            "python": sys.executable,
            "venv_realpath": str(
                pathlib.Path("/home/evan/.local/share/live/worlds/v1/runtime/venv").resolve()
            ),
        },
    )

    meminfo = {}
    for line in pathlib.Path("/proc/meminfo").read_text().splitlines():
        key, _, value = line.partition(":")
        if key in {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}:
            meminfo[key] = value.strip()
    psi = {}
    for name in ("cpu", "memory", "io"):
        path = pathlib.Path("/proc/pressure") / name
        if path.exists():
            psi[name] = path.read_text().strip()
    emit(
        "HOST",
        {
            "loadavg": pathlib.Path("/proc/loadavg").read_text().strip(),
            "meminfo": meminfo,
            "psi": psi,
            "top_cpu": run(["ps", "-eo", "pid,ppid,%cpu,%mem,rss,etimes,comm", "--sort=-%cpu"])[
                "stdout"
            ].splitlines()[:12],
            "top_rss": run(["ps", "-eo", "pid,ppid,%cpu,%mem,rss,etimes,comm", "--sort=-rss"])[
                "stdout"
            ].splitlines()[:12],
        },
    )

    emit(
        "SERVICES",
        {
            "user_daemon_manager_active": run(
                ["systemctl", "--user", "is-active", "daemon_manager.service"]
            ),
            "user_daemon_manager_status": run(
                [
                    "systemctl",
                    "--user",
                    "status",
                    "daemon_manager.service",
                    "--no-pager",
                    "--lines=12",
                ]
            ),
            "system_daemon_manager_active": run(
                ["systemctl", "is-active", "daemon_manager.service"]
            ),
            "supervisor_status": run(
                [
                    "/home/evan/.local/share/live/worlds/v1/runtime/venv/bin/supervisorctl",
                    "-c",
                    "/home/evan/.local/share/live/daemon_manager/supervisor/supervisord.conf",
                    "status",
                ]
            ),
            "owner_processes": run(
                [
                    "bash",
                    "-lc",
                    "ps -eo pid,ppid,etimes,%cpu,%mem,comm,args | "
                    "grep -E 'daemon_manager|selected.*world|world.*adopt|runtime_reconciler|employee_runtime|ecr_email|human_operator_panel|computerusex' | "
                    "grep -v grep | head -80",
                ]
            ),
        },
    )

    modules = {}
    for name in ("ecr_email", "employee_runtime", "human_operator_panel", "daemon_manager"):
        row: dict[str, Any] = {}
        try:
            module = importlib.import_module(name)
            path = str(pathlib.Path(module.__file__).resolve())
            row.update(import_ok=True, file=path, sha256=sha(path))
            for dist in (name, name.replace("_", "-")):
                try:
                    row["version"] = importlib.metadata.version(dist)
                    break
                except Exception:
                    pass
        except Exception as exc:
            row.update(import_ok=False, error=f"{type(exc).__name__}: {exc}")
        modules[name] = row
    emit("LOADED_MODULES", modules)

    repos = (
        "/home/evan/Projects/static_and_singular/internal_sub_projects/ecr_email",
        "/home/evan/Projects/worlds/v1/cognilode/internal_sub_projects/autonomy_core/internal_sub_projects/employee",
        "/home/evan/Projects/static_and_singular/internal_sub_projects/human_operator_panel",
        "/home/evan/Projects/static_and_singular/internal_sub_projects/daemon_manager",
        "/home/evan/Projects/everything",
        "/home/evan/Projects/static_and_singular",
    )
    repo_rows = {}
    for repo in repos:
        path = pathlib.Path(repo)
        if not path.exists():
            repo_rows[repo] = {"exists": False}
            continue
        repo_rows[repo] = {
            "exists": True,
            "head": run(["git", "-C", repo, "rev-parse", "HEAD"])["stdout"].strip(),
            "branch": run(["git", "-C", repo, "branch", "--show-current"])["stdout"].strip(),
            "status": run(["git", "-C", repo, "status", "--short"])["stdout"].splitlines()[:24],
        }
    emit("SOURCE_REPOS", repo_rows)

    emit(
        "ADOPTION_SEARCH",
        run(
            [
                "bash",
                "-lc",
                "grep -RIl -E 'selected.?world.*adopt|adopt.*selected.?world|selected_runtime.*reconcil' "
                "/home/evan/Projects/static_and_singular/internal_sub_projects/daemon_manager "
                "/home/evan/Projects/static_and_singular/internal_sub_projects/shared_venv_manager "
                "/home/evan/Projects/worlds/v1/cognilode/internal_sub_projects/autonomy_core/internal_sub_projects/employee "
                "2>/dev/null | head -80",
            ],
            timeout=15,
        ),
    )

    cdp_hop: dict[str, Any] = {}
    try:
        with urllib.request.urlopen("http://127.0.0.1:9331/json/list", timeout=3) as response:
            pages = json.load(response)
        cdp_hop["cdp"] = {
            "responsive": True,
            "page_count": sum(1 for item in pages if item.get("type") == "page"),
            "conversation_page_count": sum(
                1
                for item in pages
                if item.get("type") == "page" and "/c/" in str(item.get("url") or "")
            ),
        }
    except Exception as exc:
        cdp_hop["cdp"] = {"responsive": False, "error": f"{type(exc).__name__}: {exc}"}
    try:
        with urllib.request.urlopen(
            "http://127.0.0.1:8765/evidence-neighborhood", timeout=4
        ) as response:
            body = response.read()
        text = body.decode("utf-8", "replace")
        cdp_hop["hop"] = {
            "http_ok": True,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "surface_v3_present": "EVIDENCE_NEIGHBORHOOD_CAUSAL_V3" in text,
            "candidate_snapshot_ids": re.findall(r"[0-9a-f]{20}", text)[:6],
        }
    except Exception as exc:
        cdp_hop["hop"] = {"http_ok": False, "error": f"{type(exc).__name__}: {exc}"}
    emit("CDP_HOP", cdp_hop)

    for path in (
        "/home/evan/Projects/static_and_singular/internal_sub_projects/ecr_email/src",
        "/home/evan/Projects/worlds/v1/cognilode/internal_sub_projects/autonomy_core/internal_sub_projects/employee/src",
        "/home/evan/Projects/static_and_singular/internal_sub_projects/contracts_commands_and_tools/src",
        "/home/evan/Projects/static_and_singular/internal_sub_projects/secretary/src",
        "/home/evan/Projects/static_and_singular/internal_sub_projects/persona_sot/src",
        "/home/evan/Projects/static_and_singular/src",
    ):
        if path not in sys.path:
            sys.path.insert(0, path)
    try:
        from ecr_email.daemon import _domain_root
        from ecr_email.material_delegation import stage_and_delegate
        from ecr_email.poll import poll_all_once

        root = _domain_root()
        polled = poll_all_once(root=root, persist=True, limit=100)
        material = dict(polled.get("material_watch") or {})
        emitted = [dict(item) for item in material.get("emitted") or () if isinstance(item, dict)]
        delegated = stage_and_delegate(emitted, root=root)
        blob = json.dumps(emitted, sort_keys=True, default=str)
        emit(
            "LOADED_ECR_BLACK_BOX",
            {
                "new_count": polled.get("new_count"),
                "inbox_new_count": (polled.get("inbox") or {}).get("new_count"),
                "sent_new_count": (polled.get("sent") or {}).get("new_count"),
                "material_emitted_count": len(emitted),
                "matched_current_correlations": [
                    correlation for correlation in (REPAIR, REVENUE) if correlation in blob
                ],
                "delegation_status": delegated.get("status"),
                "delegation_state": delegated.get("state"),
                "delegated_count": delegated.get("delegated_count"),
                "pending_count": delegated.get("pending_count"),
            },
        )
    except Exception as exc:
        emit("LOADED_ECR_BLACK_BOX", {"error": f"{type(exc).__name__}: {exc}"})

    emit(
        "ACTIVATIONS",
        {
            persona: compact_activation(persona)
            for persona in ("everything", "static_and_singular", "cognilode", "business")
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
