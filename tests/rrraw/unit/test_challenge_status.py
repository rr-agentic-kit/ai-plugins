"""Challenge attestation: three-state stamp/invalidate and mint_hash exclusion."""

from __future__ import annotations

import validate_planning_script as vp


def _status_with_digests() -> dict:
    status = vp.default_unfrozen_status(1)
    status["levels"]["prd"]["digest"] = "sha256:prd"
    status["levels"]["frd"]["digest"] = "sha256:frd"
    status["levels"]["mrd"]["digest"] = "sha256:mrd"
    return status


def test_mint_hash_excludes_challenge_and_meta_keys() -> None:
    status = vp.default_unfrozen_status(1)
    baseline = vp.compute_mint_hash(status)
    payload = vp.canonical_mint_payload(status)
    for key in vp.MINT_EXCLUDED_KEYS:
        assert key not in payload
    status["challenge"] = {"prd": {"status": "clean", "scanned_digest": "sha256:prd"}}
    status["next_challenge"] = {"prd": {"status": "dirty", "scanned_digest": None}}
    status["claude_config_version"] = 99
    status["product_status"] = "shipped"
    assert vp.compute_mint_hash(status) == baseline


def test_fill_status_missing_challenge_does_not_change_mint_hash() -> None:
    status = vp.default_unfrozen_status(1)
    recorded = status["mint_hash"]
    del status["challenge"]
    del status["next_challenge"]
    payload_changed, meta_changed = vp.fill_status_missing(status, 1)
    assert payload_changed is False
    assert meta_changed is True
    assert status["challenge"] == {}
    assert status["next_challenge"] == {}
    assert status["mint_hash"] == recorded
    assert vp.compute_mint_hash(status) == recorded


def test_fill_replaces_null_challenge_map() -> None:
    status = vp.default_unfrozen_status(1)
    status["challenge"] = None
    status["next_challenge"] = "bogus"
    _, meta_changed = vp.fill_status_missing(status, 1)
    assert meta_changed is True
    assert status["challenge"] == {}
    assert status["next_challenge"] == {}


def test_stamp_clean_and_dirty_from_doc_stem() -> None:
    status = _status_with_digests()
    vp.stamp_challenge_status(
        status,
        [{"id": "bs-001", "doc": "prd", "doc_ref": "prd.md § goals"}],
        ["prd.md", "frd.md", "mrd.md"],
    )
    assert status["challenge"]["prd"] == {
        "status": "dirty",
        "scanned_digest": "sha256:prd",
    }
    assert status["challenge"]["frd"] == {
        "status": "clean",
        "scanned_digest": "sha256:frd",
    }
    assert status["challenge"]["mrd"] == {
        "status": "clean",
        "scanned_digest": "sha256:mrd",
    }
    assert "exec-summary" not in status["challenge"]


def test_stamp_zero_findings_all_reviewed_clean() -> None:
    status = _status_with_digests()
    vp.stamp_challenge_status(status, [], ["prd.md", "frd.md"])
    assert status["challenge"]["prd"]["status"] == "clean"
    assert status["challenge"]["frd"]["status"] == "clean"
    assert status["challenge"]["prd"]["scanned_digest"] == "sha256:prd"


def test_stamp_falls_back_to_doc_ref_stem() -> None:
    status = _status_with_digests()
    vp.stamp_challenge_status(
        status,
        [{"id": "bs-002", "doc_ref": "frd.md § 3.2"}],
        ["frd.md"],
    )
    assert status["challenge"]["frd"]["status"] == "dirty"


def test_invalidate_compose_dirties_clean_and_accepted() -> None:
    status = _status_with_digests()
    status["challenge"] = {
        "prd": {"status": "clean", "scanned_digest": "sha256:prd"},
        "frd": {"status": "dirty-accepted", "scanned_digest": "sha256:frd"},
        "mrd": {"status": "dirty", "scanned_digest": "sha256:mrd"},
    }
    vp.invalidate_challenge_on_compose(status, "prd")
    vp.invalidate_challenge_on_compose(status, "frd")
    vp.invalidate_challenge_on_compose(status, "mrd")
    vp.invalidate_challenge_on_compose(status, "exec-summary")
    assert status["challenge"]["prd"]["status"] == "dirty"
    assert status["challenge"]["frd"]["status"] == "dirty"
    assert status["challenge"]["mrd"]["status"] == "dirty"
    assert "exec-summary" not in status["challenge"]


def test_dirty_accepted_re_dirties_on_digest_change() -> None:
    status = _status_with_digests()
    vp.accept_challenge_residual(status, ["prd"])
    assert status["challenge"]["prd"]["status"] == "dirty-accepted"
    assert status["challenge"]["prd"]["scanned_digest"] == "sha256:prd"
    status["levels"]["prd"]["digest"] = "sha256:prd-moved"
    vp.invalidate_challenge_on_digest_change(status)
    assert status["challenge"]["prd"]["status"] == "dirty"


def test_dirty_accepted_same_digest_stays() -> None:
    status = _status_with_digests()
    vp.accept_challenge_residual(status, ["prd"])
    vp.invalidate_challenge_on_digest_change(status)
    assert status["challenge"]["prd"]["status"] == "dirty-accepted"


def test_next_challenge_mirrors_next_levels() -> None:
    status = vp.default_unfrozen_status(1)
    status["next_levels"]["prd"] = {
        "rev": "?",
        "digest": "sha256:next-prd",
        "pins": {},
    }
    vp.stamp_challenge_status(
        status,
        [{"id": "bs-001", "doc": "prd"}],
        ["prd.md"],
        next_track=True,
    )
    assert status["challenge"] == {}
    assert status["next_challenge"]["prd"]["status"] == "dirty"
    assert status["next_challenge"]["prd"]["scanned_digest"] == "sha256:next-prd"
    vp.invalidate_challenge_on_compose(status, "prd", next_track=True)
    assert status["next_challenge"]["prd"]["status"] == "dirty"
