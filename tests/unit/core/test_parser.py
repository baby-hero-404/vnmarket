from datetime import date

import pytest

from vnmarket.core.utils import parser as p

REF = date(2024, 1, 10)  # 3rd Thursday of Jan 2024 is the 18th


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("CurrencyCode", "currency_code"),
        ("buyCash", "buy_cash"),
        ("HTTPServer", "http_server"),
    ],
)
def test_camel_to_snake(raw, expected):
    assert p.camel_to_snake(raw) == expected


def test_remove_vietnamese_accents():
    assert p.remove_vietnamese_accents("Đồng Nai Việt Nam") == "Dong Nai Viet Nam"


def test_snake_case_normalizers():
    assert p.normalize_vietnamese_text_to_snake_case("Lợi nhuận sau thuế") == (
        "loi_nhuan_sau_thue"
    )
    assert p.normalize_english_text_to_snake_case("Net Profit (Loss)") == (
        "net_profit_loss"
    )


def test_is_valid_identifier():
    assert p.is_valid_identifier("abc")
    assert not p.is_valid_identifier("1abc")


def test_flatten_data():
    assert p.flatten_data({"a": {"b": 1}, "c": 2}) == {"a_b": 1, "c": 2}


@pytest.mark.parametrize(
    "symbol, kind",
    [
        ("FPT", "stock"),
        ("VNINDEX", "index"),
        ("VN30F2406", "derivative"),
        ("VN30F1M", "derivative"),
        ("CFPT2401", "coveredWarr"),
    ],
)
def test_get_asset_type(symbol, kind):
    assert p.get_asset_type(symbol) == kind


class TestVn30Contracts:
    def test_expand_relative_month_and_quarter(self):
        assert p.vn30_expand_contract("VN30F1M", REF) == "VN30F2401"
        assert p.vn30_expand_contract("VN30F2Q", REF) == "VN30F2406"

    def test_expand_rejects_explicit_symbol(self):
        with pytest.raises(ValueError, match="Invalid abbrev"):
            p.vn30_expand_contract("VN30F2406", REF)

    def test_abbrev_next_month_is_2m(self):
        assert p.vn30_abbrev_contract("VN30F2402", REF) == "VN30F2M"


class TestMaturity:
    def test_explicit_is_third_thursday(self):
        assert p.get_derivative_maturity_date("F2402") == date(2024, 2, 15)

    def test_f1m_before_expiry_stays_in_month(self):
        assert p.get_derivative_maturity_date("F1M", REF) == date(2024, 1, 18)

    def test_f1m_after_expiry_rolls_over(self):
        assert p.get_derivative_maturity_date("F1M", date(2024, 1, 25)) == date(
            2024, 2, 15
        )

    def test_f1q_picks_next_quarter_month(self):
        assert p.get_derivative_maturity_date("F1Q", REF) == date(2024, 3, 21)

    def test_f1q_wraps_to_next_year(self):
        assert p.get_derivative_maturity_date("F1Q", date(2024, 12, 25)) == date(
            2025, 3, 20
        )


class TestConvertDerivative:
    def test_krx_code(self):
        assert p.convert_derivative_symbol("VN30F2402", REF) == "41I1E2000"
        assert p.convert_derivative_symbol("VN30F1M", REF) == "41I1E1000"

    def test_unknown_underlying(self):
        with pytest.raises(ValueError, match="Unknown underlying"):
            p.convert_derivative_symbol("ABC2402", REF)
