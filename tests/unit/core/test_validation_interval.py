from datetime import datetime

import pytest

from vnmarket.core.types import TimeFrame
from vnmarket.core.utils.interval import normalize_interval
from vnmarket.core.utils.validation import (
    convert_to_timestamps,
    validate_date_range,
    validate_interval,
    validate_model_input,
    validate_pagination,
    validate_symbol,
)


class TestValidateSymbol:
    def test_uppercases_valid_symbol(self):
        assert validate_symbol("fpt") == "FPT"

    @pytest.mark.parametrize("bad", [None, 123, "ab", "A" * 13])
    def test_rejects_bad_input(self, bad):
        with pytest.raises(ValueError):
            validate_symbol(bad)

    def test_symbol_map_wins(self):
        assert validate_symbol("abc", {"ABC": "XYZ"}) == "XYZ"


class TestValidateDateRange:
    def test_end_is_inclusive(self):
        start, end = validate_date_range("2024-01-01", "2024-01-31")
        assert start == datetime(2024, 1, 1)
        assert end == datetime(2024, 2, 1)

    def test_open_end_defaults_to_future(self):
        _, end = validate_date_range("2024-01-01")
        assert end > datetime.now()

    def test_bad_format(self):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            validate_date_range("01/01/2024")

    def test_start_after_end(self):
        with pytest.raises(ValueError, match="greater"):
            validate_date_range("2024-02-01", "2024-01-01")

    def test_timestamps_ordered(self):
        s, e = convert_to_timestamps(validate_date_range("2024-01-01", "2024-01-02"))
        assert e - s == 2 * 86400


class TestMisc:
    def test_interval_map(self):
        assert validate_interval("1D", {"1D": "day"}) == "day"
        with pytest.raises(ValueError, match="Invalid interval"):
            validate_interval("2D", {"1D": "day"})

    def test_pagination(self):
        assert validate_pagination(250, max_page_size=100) == (100, 3)
        assert validate_pagination(50) == (50, 1)
        with pytest.raises(ValueError):
            validate_pagination(0)
        with pytest.raises(ValueError):
            validate_pagination(10, page=-1)

    def test_model_input(self):
        validate_model_input({"a": 1}, ["a"])
        with pytest.raises(ValueError, match="b"):
            validate_model_input({"a": 1}, ["a", "b"])


class TestNormalizeInterval:
    def test_none_is_daily(self):
        assert normalize_interval(None) == TimeFrame.DAY_1

    def test_enum_passthrough(self):
        assert normalize_interval(TimeFrame.DAY_1) == TimeFrame.DAY_1

    @pytest.mark.parametrize("raw", ["1D", "d", "day"])
    def test_daily_aliases(self, raw):
        assert normalize_interval(raw) == TimeFrame.DAY_1

    def test_month_is_case_sensitive(self):
        assert normalize_interval("1M") == TimeFrame.MONTH_1
        assert normalize_interval("1m") == TimeFrame.MINUTE_1
