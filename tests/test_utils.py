import os
import pytest
from unittest.mock import patch

from openclaw_acp.utils import require_api_key


class TestRequireApiKey:
    def test_raises_when_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):

            @require_api_key("OPENCLAW_GATEWAY_TOKEN")
            def dummy_func(openclaw_gateway_token=None):
                return "success"

            with pytest.raises(ValueError, match="API key 'OPENCLAW_GATEWAY_TOKEN'"):
                dummy_func()

    def test_passes_when_api_key_in_kwargs(self):
        @require_api_key("OPENCLAW_GATEWAY_TOKEN")
        def dummy_func(openclaw_gateway_token=None):
            return openclaw_gateway_token

        result = dummy_func(openclaw_gateway_token="test_token")
        assert result == "test_token"

    def test_passes_when_api_key_in_env(self):
        with patch.dict(os.environ, {"OPENCLAW_GATEWAY_TOKEN": "env_token"}):

            @require_api_key("OPENCLAW_GATEWAY_TOKEN")
            def dummy_func(openclaw_gateway_token=None):
                return "success"

            result = dummy_func()
            assert result == "success"

    def test_kwarg_overrides_env(self):
        with patch.dict(os.environ, {"OPENCLAW_GATEWAY_TOKEN": "env_token"}):

            @require_api_key("OPENCLAW_GATEWAY_TOKEN")
            def dummy_func(openclaw_gateway_token=None):
                return openclaw_gateway_token

            result = dummy_func(openclaw_gateway_token="kwargs_token")
            assert result == "kwargs_token"
