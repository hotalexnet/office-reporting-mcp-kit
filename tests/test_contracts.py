from __future__ import annotations

import json
import unittest
from pathlib import Path

from office_reporting.contracts import (
    FORBIDDEN_MODEL_ARGS,
    ModelControlledFieldError,
    reject_model_controlled_fields,
)
from office_reporting.replay import ReplayCheck, ReplayRejected, require_replay_guard


ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_manifest_forbidden_args_match_python_constant(self) -> None:
        manifest = json.loads(
            (ROOT / "contracts" / "office-reporting-mcp.manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(set(manifest["forbidden_model_args"]), FORBIDDEN_MODEL_ARGS)

    def test_reject_model_controlled_fields_rejects_forbidden(self) -> None:
        with self.assertRaises(ModelControlledFieldError):
            reject_model_controlled_fields(
                {"report_type": "example_report", "storage_key": "x"},
                allowed_args={"report_type"},
            )

    def test_reject_model_controlled_fields_rejects_unknown(self) -> None:
        with self.assertRaises(ModelControlledFieldError):
            reject_model_controlled_fields(
                {"report_type": "example_report", "surprise": "x"},
                allowed_args={"report_type"},
            )

    def test_replay_guard_skips_trusted_gateway_key(self) -> None:
        require_replay_guard(
            transport_auth_mode="trusted-gateway-key",
            replay=ReplayCheck(request_nonce=None, request_timestamp=None),
            shared_nonce_store_configured=False,
        )

    def test_replay_guard_fails_closed_without_store(self) -> None:
        with self.assertRaises(ReplayRejected):
            require_replay_guard(
                transport_auth_mode="hmac",
                replay=ReplayCheck(request_nonce="n", request_timestamp=1784010000),
                shared_nonce_store_configured=False,
            )


if __name__ == "__main__":
    unittest.main()

