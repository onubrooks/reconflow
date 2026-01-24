"""Tests for normalization utilities."""

from reconflow.normalize import standardize_decimal, normalize_reference
from reconflow.normalize.decimal import amounts_match


class TestDecimalStandardization:
    """Tests for decimal standardization."""

    def test_basic_rounding(self):
        """Test basic rounding to 2 decimal places."""
        assert standardize_decimal(10.007, 2) == 10.01
        assert standardize_decimal(10.004, 2) == 10.00
        assert standardize_decimal(10.005, 2) == 10.01

    def test_string_input(self):
        """Test handling string inputs."""
        assert standardize_decimal("10.007", 2) == 10.01
        assert standardize_decimal("100.994", 2) == 100.99

    def test_none_input(self):
        """Test handling None input."""
        assert standardize_decimal(None) is None

    def test_integer_input(self):
        """Test handling integer inputs."""
        assert standardize_decimal(100, 2) == 100.00

    def test_different_precision(self):
        """Test different precision levels."""
        assert standardize_decimal(10.1234, 3) == 10.123
        assert standardize_decimal(10.1236, 3) == 10.124

    def test_amounts_match_exact(self):
        """Test exact amount matching."""
        assert amounts_match(10.00, 10.00) is True
        assert amounts_match(10.01, 10.00) is False

    def test_amounts_match_with_tolerance(self):
        """Test amount matching with tolerance."""
        assert amounts_match(10.00, 10.01, tolerance=0.01) is True
        assert amounts_match(10.00, 10.02, tolerance=0.01) is False


class TestReferenceNormalization:
    """Tests for reference normalization."""

    def test_basic_normalization(self):
        """Test basic reference normalization."""
        assert normalize_reference("TRF|ABC|123") == "TRF|ABC|123"
        assert normalize_reference("trf|abc|123") == "TRF|ABC|123"

    def test_whitespace_handling(self):
        """Test whitespace is handled correctly."""
        assert normalize_reference("  TRF|ABC|123  ") == "TRF|ABC|123"
        assert normalize_reference("TRF | ABC | 123") == "TRF | ABC | 123"

    def test_none_input(self):
        """Test handling None input."""
        assert normalize_reference(None) == ""

    def test_empty_string(self):
        """Test handling empty string."""
        assert normalize_reference("") == ""
        assert normalize_reference("   ") == ""

    def test_extract_embedded_reference(self):
        """Test extracting TRF pattern from longer string."""
        result = normalize_reference("Payment: TRF|MONIEPOINT|123 confirmed")
        assert result == "TRF|MONIEPOINT|123"

    def test_no_extraction_when_disabled(self):
        """Test that extraction can be disabled."""
        result = normalize_reference("Payment: TRF|ABC|123", extract_trf=False)
        assert result == "PAYMENT: TRF|ABC|123"
