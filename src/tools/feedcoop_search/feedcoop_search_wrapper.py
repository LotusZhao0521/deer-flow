import json
import os
from typing import List, Optional

import requests
from pydantic import BaseModel, Field


class FeedcoopSearchResponse(BaseModel):
    """The structure of the Feedcoop web search response"""

    result_count: int = Field(alias="ResultCount")
    web_results: List["WebItem"] = Field(alias="WebResults")
    search_context: "SearchContext" = Field(alias="SearchContext")

    class WebItem(BaseModel):
        id: str = Field(alias="Id")
        sort_id: int = Field(alias="SortId")
        title: str = Field(alias="Title")
        site_name: Optional[str] = Field(alias="SiteName")
        url: Optional[str] = Field(alias="Url")
        snippet: str = Field(alias="Snippet")
        summary: Optional[str] = Field(alias="Summary")
        content: Optional[str] = Field(alias="Content")
        publish_time: Optional[str] = Field(alias="PublishTime", description="like `2025-05-30T19:35:24+08:00`")
        logo_url: Optional[str] = Field(alias="LogoUrl")
        rank_score: Optional[float] = Field(alias="RankScore")
        auth_info_des: str = Field(alias="AuthInfoDes")
        auth_info_level: Optional[int] = Field(alias="AuthInfoLevel")

    class SearchContext(BaseModel):
        search_type: str = Field(alias="SearchType")
        origin_query: str = Field(alias="OriginQuery")


class FeedcoopSearchWrapper(BaseModel):
    """Warpper around the Feedcoopapi web search engine."""

    api_key: str
    """The API key to use for the Feedcoopapi web search engine."""
    search_kwargs: dict = Field(default_factory=dict)
    """Additional keyword arguments to pass to the search request."""
    base_url: str = "https://open.feedcoopapi.com/search_api/web_search"
    """The base URL for the Feedcoopapi web search engine."""

    def run(self, query: str) -> str:
        """Query the Feedcoop web search engine and return the results as a JSON string.

        Args:
            query (str): The query to search for

        Returns:
            str: The results as a JSON string
        """
        web_search_response = self._search_request(query=query)
        final_response = FeedcoopSearchResponse(**web_search_response)
        return final_response.model_dump_json()

    def _search_request(self, query: str) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        req = requests.PreparedRequest()
        params = {**self.search_kwargs, **{"q": query}}
        req.prepare_url(self.base_url, params)
        if req.url is None:
            raise ValueError("prepared url must not be None")

        response = requests.post(req.url, headers=headers)
        if not response.ok:
            raise Exception(f"HTTP error {response.status_code}")

        return response.json()


if __name__ == "__main__":
    response = FeedcoopSearchWrapper(
        api_key=os.getenv("FEEDCOOP_SEARCH_API_KEY", ""), search_kwargs={"SearchType": True}
    ).run("北京坐标")
    print(response)
