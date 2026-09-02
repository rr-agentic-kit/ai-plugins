"""Tests for humanize helper CLI."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLI = SCRIPTS_DIR / "cli.py"


def run_cli(*args: str, input_text: str | None = None) -> dict:
    cmd = [sys.executable, str(CLI), *args]
    result = subprocess.run(
        cmd,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
        cwd=SCRIPTS_DIR,
    )
    if result.returncode == 2:
        raise RuntimeError(f"usage error: {result.stderr}")
    payload = json.loads(result.stdout)
    return payload


class TestScan(unittest.TestCase):
    def test_ai_paragraph_hits_expected_categories(self) -> None:
        payload = run_cli("scan", str(FIXTURES / "ai_paragraph.txt"))
        self.assertTrue(payload["ok"])
        hits = payload["result"]["hits"]
        self.assertIn("filler", hits)
        self.assertIn("banned_word", hits)
        self.assertIn("copula_avoidance", hits)
        self.assertIn("chatbot", hits)
        self.assertTrue(payload["result"]["needs_judgment"])
        self.assertTrue(payload["result"]["auto_fixable"])

    def test_scan_stdin(self) -> None:
        text = "In order to test, we run scan."
        payload = run_cli("scan", input_text=text)
        self.assertTrue(payload["ok"])
        self.assertIn("filler", payload["result"]["hits"])


class TestApplySafe(unittest.TestCase):
    def test_golden_apply_safe(self) -> None:
        input_path = FIXTURES / "apply_safe_input.txt"
        expected = (FIXTURES / "apply_safe_expected.txt").read_text(encoding="utf-8")
        payload = run_cli("apply-safe", str(input_path))
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["result"]["changed"])
        self.assertEqual(payload["result"]["text"].strip(), expected.strip())

    def test_dry_run_preview(self) -> None:
        payload = run_cli(
            "apply-safe",
            "--dry-run",
            str(FIXTURES / "apply_safe_input.txt"),
        )
        self.assertTrue(payload["ok"])
        self.assertIn("preview", payload["result"])
        self.assertNotIn("text", payload["result"])


class TestSuggestRegister(unittest.TestCase):
    def test_warm_you_register(self) -> None:
        payload = run_cli("suggest-register", str(FIXTURES / "warm_you.txt"))
        self.assertTrue(payload["ok"])
        result = payload["result"]
        self.assertEqual(result["voice"], "you")
        self.assertIn(result["tone"], ("warm", "plain"))
        self.assertGreaterEqual(result["confidence"], 0.5)


class TestEnvelope(unittest.TestCase):
    def test_empty_input_fails(self) -> None:
        payload = run_cli("scan", input_text="   ")
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "empty_input")


if __name__ == "__main__":
    unittest.main()
