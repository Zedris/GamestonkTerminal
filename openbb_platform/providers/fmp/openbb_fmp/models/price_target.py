"""FMP Equity Ownership Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target import (
    PriceTargetData,
    PriceTargetQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_urls
from pydantic import Field, field_validator


class FMPPriceTargetQueryParams(PriceTargetQueryParams):
    """FMP Price Target Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Price-Target
    """

    with_grade: bool = Field(
        False,
        description="Include upgrades and downgrades in the response.",
    )


class FMPPriceTargetData(PriceTargetData):
    """FMP Price Target Data."""

    __alias_dict__ = {
        "analyst_firm": "gradingCompany",
        "rating_current": "newGrade",
        "rating_previous": "previousGrade",
        "news_title": "newsTitle",
        "url_news": "newsURL",
        "url_base": "newsBaseURL",
    }

    news_url: Optional[str] = Field(
        default=None, description="News URL of the price target."
    )
    news_title: Optional[str] = Field(
        default=None, description="News title of the price target."
    )
    news_publisher: Optional[str] = Field(
        default=None, description="News publisher of the price target."
    )
    news_base_url: Optional[str] = Field(
        default=None, description="News base URL of the price target."
    )

    @field_validator("published_date", mode="before", check_fields=False)
    def validate_date(cls, v: str):  # pylint: disable=E0213
        """Validate the published date."""
        v = v.replace("\n", "")
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")  # type: ignore


class FMPPriceTargetFetcher(
    Fetcher[
        FMPPriceTargetQueryParams,
        List[FMPPriceTargetData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPPriceTargetQueryParams:
        """Transform the query params."""
        return FMPPriceTargetQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPPriceTargetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        endpoint = "upgrades-downgrades" if query.with_grade else "price-target"

        urls = []
        for symbol in query.symbol.split(","):
            query.symbol = symbol
            urls.append(create_url(4, endpoint, api_key, query, exclude=["limit"]))

        return await get_data_urls(urls)

    @staticmethod
    def transform_data(
        query: FMPPriceTargetQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPPriceTargetData]:
        """Return the transformed data."""
        results: List[FMPPriceTargetData] = []
        for item in data:
            new_item = {
                k if k != "analystCompany" else "analyst_firm": v
                for k, v in item.items()
            }
            results.append(FMPPriceTargetData.model_validate(new_item))
        return results
