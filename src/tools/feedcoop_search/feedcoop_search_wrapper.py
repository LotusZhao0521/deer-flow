import json
import os
from typing import List, Optional, Literal
from langchain_core.documents import Document

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


class FeedcoopSearchAdditionalParams(BaseModel):
    search_type: Literal["web", "web_summary"] = Field(alias="SearchType", default="web")
    count: int = Field(alias="Count", default=10, description="number of search items, the max is 50")
    filter: Optional["Filter"] = Field(alias="Filter", default=None)
    need_summary: bool = Field(alias="NeedSummary", default=False)
    time_range: str = Field(
        alias="TimeRange",
        default="",
        description="Specify the publication time for the search, The following enumeration values: -OneDay -OneWeek -OneMonth -OneYear -YYYY-MM-DD..YYYY-MM-DD",
    )

    class Filter(BaseModel):
        need_content: bool = Field(alias="NeedContent", default=False, description="only return results with body text")
        need_url: bool = Field(
            alias="NeedUrl", default=False, description="only return the results of the original link"
        )
        sites: str = Field(
            alias="Sites",
            default="",
            description="Specify the scope of the search site, separate multiple domains with '|', and support up to 5.",
        )


class FeedcoopSearchWrapper(BaseModel):
    """Warpper around the Feedcoopapi web search engine."""

    api_key: str
    """The API key to use for the Feedcoopapi web search engine."""
    search_kwargs: FeedcoopSearchAdditionalParams | dict | None
    """Additional keyword arguments to pass to the search request."""
    base_url: str = "https://open.feedcoopapi.com/search_api/web_search"
    """The base URL for the Feedcoopapi web search engine."""

    def run(self, query: str) -> str:
        """Query the Feedcoop web search engine and return the results as a structure.

        Args:
            query (str): The query to search for

        Returns:
            str: The results as a structure
        """
        web_search_response = self._search_request(query)
        final_response = FeedcoopSearchResponse(**web_search_response["Result"])
        return final_response.model_dump_json()

    def _search_request(self, query: str) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        req = requests.PreparedRequest()
        body = {**self.search_kwargs.model_dump(by_alias=True), **{"Query": query}}
        req.prepare_url(self.base_url, {})
        if req.url is None:
            raise ValueError("prepared url must not be None")

        response = requests.post(req.url, json=body, headers=headers)
        response_json = response.json()
        if not response.ok:
            raise Exception(f"HTTP error {response.status_code}")
        if "Error" in response_json["ResponseMetadata"]:
            error_code = response_json["ResponseMetadata"]["Error"]["CodeN"]
            message = response_json["ResponseMetadata"]["Error"]["Message"]
            raise Exception(f"API request failed, error code: {error_code}, message: {message}")

        return response_json


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("FEEDCOOP_API_KEY", "")
    result = FeedcoopSearchWrapper(api_key=api_key, search_kwargs={"Count": 1}).run("北京有什么好玩的")
    print(result)
