"""Tests for agentpilot.domain.common boundary-validation primitives."""

from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from agentpilot.domain.common import (
    canonical_json,
    deep_freeze,
    FrozenMapping,
    require_aware,
    require_text,
    stable_id,
    utc_now,
)


class TestRequireText:
    def test_strips_whitespace(self):
        assert require_text("  hello  ", "f") == "hello"

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="must be a non-empty string"):
            require_text("", "field")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="must be a non-empty string"):
            require_text("   ", "field")

    def test_non_string_raises(self):
        with pytest.raises(ValueError, match="must be a non-empty string"):
            require_text(123, "field")  # type: ignore[arg-type]

    def test_none_raises(self):
        with pytest.raises(ValueError, match="must be a non-empty string"):
            require_text(None, "field")  # type: ignore[arg-type]

    def test_normal_text_passthrough(self):
        assert require_text("world", "f") == "world"


class TestRequireAware:
    def test_aware_datetime_passes(self):
        dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
        assert require_aware(dt, "ts") is dt

    def test_naive_datetime_raises(self):
        with pytest.raises(ValueError, match="must be a timezone-aware"):
            require_aware(datetime(2026, 1, 1), "ts")

    def test_non_datetime_raises(self):
        with pytest.raises(ValueError, match="must be a timezone-aware"):
            require_aware("2026-01-01", "ts")  # type: ignore[arg-type]


class TestFrozenMapping:
    def test_read_access(self):
        fm = FrozenMapping({"a": 1, "b": 2})
        assert fm["a"] == 1
        assert len(fm) == 2

    def test_immutable(self):
        fm = FrozenMapping({"x": 1})
        with pytest.raises(TypeError):
            fm["x"] = 99  # type: ignore[index]

    def test_nested_freeze(self):
        fm = FrozenMapping({"inner": {"deep": [1, 2]}})
        assert isinstance(fm["inner"], FrozenMapping)
        assert isinstance(fm["inner"]["deep"], tuple)

    def test_iteration(self):
        fm = FrozenMapping({"a": 1, "b": 2})
        assert set(fm) == {"a", "b"}

    def test_empty(self):
        fm = FrozenMapping()
        assert len(fm) == 0

    def test_deepcopy_returns_self(self):
        import copy
        fm = FrozenMapping({"k": "v"})
        assert copy.deepcopy(fm) is fm


class TestDeepFreeze:
    def test_dict_becomes_frozen_mapping(self):
        result = deep_freeze({"a": 1})
        assert isinstance(result, FrozenMapping)

    def test_list_becomes_tuple(self):
        result = deep_freeze([1, 2, 3])
        assert isinstance(result, tuple)
        assert result == (1, 2, 3)

    def test_set_becomes_frozenset(self):
        result = deep_freeze({1, 2})
        assert isinstance(result, frozenset)

    def test_nested(self):
        result = deep_freeze({"items": [{"x": 1}]})
        assert isinstance(result, FrozenMapping)
        assert isinstance(result["items"], tuple)
        assert isinstance(result["items"][0], FrozenMapping)

    def test_already_frozen_is_identity(self):
        fm = FrozenMapping({"k": "v"})
        assert deep_freeze(fm) is fm

    def test_scalar_passthrough(self):
        assert deep_freeze(42) == 42
        assert deep_freeze("hello") == "hello"


class TestCanonicalJson:
    def test_sorted_keys(self):
        result = canonical_json({"b": 2, "a": 1})
        assert result == '{"a":1,"b":2}'

    def test_datetime_serialized_as_utc_iso(self):
        jst = timezone(timedelta(hours=9))
        dt = datetime(2026, 1, 1, 9, 0, 0, tzinfo=jst)
        result = canonical_json(dt)
        assert "2026-01-01T00:00:00" in result

    def test_nan_raises(self):
        with pytest.raises(ValueError, match="NaN"):
            canonical_json(float("nan"))

    def test_negative_zero_normalized(self):
        result = canonical_json(-0.0)
        assert result == "0.0"


class TestStableId:
    def test_deterministic(self):
        a = stable_id("test", {"x": 1})
        b = stable_id("test", {"x": 1})
        assert a == b

    def test_prefix(self):
        result = stable_id("kind", "data")
        assert result.startswith("kind-")

    def test_different_input_different_id(self):
        a = stable_id("kind", "data1")
        b = stable_id("kind", "data2")
        assert a != b

    def test_no_coordinates_raises(self):
        with pytest.raises(ValueError, match="at least one coordinate"):
            stable_id("kind")

    def test_empty_kind_raises(self):
        with pytest.raises(ValueError, match="must be a non-empty string"):
            stable_id("", "data")


class TestUtcNow:
    def test_aware(self):
        dt = utc_now()
        assert dt.tzinfo is not None

    def test_utc(self):
        dt = utc_now()
        assert dt.tzinfo == timezone.utc
