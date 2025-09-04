"""Tool for Feedcoop search API."""

import logging
from typing import Any, Optional

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from .feedcoop_search_wrapper import FeedcoopSearchResponse, FeedcoopSearchWrapper

logger = logging.getLogger(__name__)


class FeedcoopSearch(BaseTool):  # type: ignore[override]
    """Tool that searches the Feedcoop search API."""

    name: str = "feedcoop_search"
    description: str = "a search engine by volcengine. useful for when you need to supplementary knowledge or factual basis. "

    search_wrapper: FeedcoopSearchWrapper

    @classmethod
    def from_api_key(
        cls, api_key: str, search_kwargs: Optional[dict] = None, **kwargs: Any
    ) -> "FeedcoopSearch":
    def from_api_key(
        cls, api_key: str, search_kwargs: Optional[dict] = None, **kwargs: Any
    ) -> "FeedcoopSearch":
        """Create a tool from an api key.

        Args:
            api_key (str): The api key to use.
            search_kwargs (Optional[dict], optional): Any additional kwargs to feedcoop search wrapper. Defaults to None.

        Returns:
            FeedcoopSearch: tool.
        """
        wrapper = FeedcoopSearchWrapper(api_key=api_key, search_kwargs=search_kwargs)
        return cls(search_wrapper=wrapper, **kwargs)

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return self.search_wrapper.run(query)
