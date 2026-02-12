from unittest.mock import patch

import pytest


class TestWsfeExtractsCuit:
    """Verify that WSFE endpoints extract the CUIT from Auth.Cuit correctly."""

    def test_extract_cuit_helper(self):
        from service.api.wsfe import _extract_cuit

        data = {"Auth": {"Cuit": 20304050607}}
        assert _extract_cuit(data) == "20304050607"

    def test_extract_cuit_string(self):
        from service.api.wsfe import _extract_cuit

        data = {"Auth": {"Cuit": "27123456789"}}
        assert _extract_cuit(data) == "27123456789"

    def test_extract_cuit_missing_raises(self):
        from service.api.wsfe import _extract_cuit

        with pytest.raises(KeyError):
            _extract_cuit({"Auth": {}})
