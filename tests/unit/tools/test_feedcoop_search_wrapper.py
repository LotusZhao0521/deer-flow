import json
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
import requests

from src.tools.feedcoop_search.feedcoop_search_wrapper import FeedcoopSearchWrapper


class TestFeedcoopSearchWrapper:
    @pytest.fixture
    def wrapper(self):
        with patch(
            "src.tools.feedcoop_search.feedcoop_search_wrapper.FeedcoopSearchWrapper"
        ):
            wrapper = FeedcoopSearchWrapper(api_key="dummy-key")
            return wrapper

    @pytest.fixture
    def mock_response_data(self):
        return {}
