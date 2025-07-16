#!/usr/bin/env python3

import os
import asyncio
import httpx
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Completion, CompletionArgument, CompletionContext
from mcp.types import PromptReference, ResourceTemplateReference

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage application lifecycle with HTTP client."""
    async with httpx.AsyncClient() as client:
        yield {"http_client": client}

# Initialize FastMCP server
mcp = FastMCP(
    name="Aiera Financial Data API",
    stateless_http=True,
    json_response=True,
    lifespan=app_lifespan
)

# Base configuration
AIERA_BASE_URL = "https://premium.aiera.com/api"
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Aiera-MCP-Server/1.0.0"
}

async def make_aiera_request(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    api_key: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Make a request to the Aiera API."""
    headers = DEFAULT_HEADERS.copy()
    headers["X-API-KEY"] = api_key
    
    url = f"{AIERA_BASE_URL}{endpoint}"
    
    response = await client.request(
        method=method,
        url=url,
        params=params,
        json=data,
        headers=headers,
        timeout=30.0
    )
    
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")
    
    return response.json()

# Events API Tools
@mcp.tool()
async def get_event_transcripts(event_ids: str) -> str:
    """Retrieve CSV file of event transcripts."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    
    # Extract API key from request context
    api_key = os.getenv("AIERA_API_KEY")
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {"event_ids": event_ids}
    
    headers = DEFAULT_HEADERS.copy()
    headers["X-API-KEY"] = api_key
    
    response = await client.get(
        f"{AIERA_BASE_URL}/events/audio/transcript/csv",
        params=params,
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve transcripts: {response.status_code}")
    
    return response.text

@mcp.tool()
async def get_event(
    event_id: str,
    pricing: Optional[bool] = None,
    linguistics: Optional[bool] = None
) -> Dict[str, Any]:
    """Retrieve a single event by ID with optional pricing and linguistics information."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {}
    if pricing is not None:
        params["pricing"] = pricing
    if linguistics is not None:
        params["linguistics"] = linguistics
    
    return await make_aiera_request(
        client, "GET", f"/events/{event_id}", api_key, params=params
    )

@mcp.tool()
async def get_events(
    bloomberg_ticker: str,
    start_date: str,
    end_date: str,
    event_type: Optional[str] = "earnings",
    modified_since: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieve events with filtering by ticker, date range, and event type."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {
        "bloomberg_ticker": bloomberg_ticker,
        "start_date": start_date,
        "end_date": end_date
    }
    
    if event_type:
        params["event_type"] = event_type
    if modified_since:
        params["modified_since"] = modified_since
    
    return await make_aiera_request(
        client, "GET", "/events", api_key, params=params
    )

# Calendar API Tools
@mcp.tool()
async def get_calendar(
    bloomberg_ticker: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_type: Optional[str] = "earnings",
    modified_since: Optional[str] = None,
    from_index: Optional[int] = None,
    size: Optional[int] = None,
    sort_key: Optional[str] = None
) -> Dict[str, Any]:
    """Fetch calendar events filtered by equity, watchlist, or other parameters."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {}
    if bloomberg_ticker:
        params["bloomberg_ticker"] = bloomberg_ticker
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if event_type:
        params["event_type"] = event_type
    if modified_since:
        params["modified_since"] = modified_since
    if from_index:
        params["from_index"] = from_index
    if size:
        params["size"] = size
    if sort_key:
        params["sort_key"] = sort_key
    
    return await make_aiera_request(
        client, "GET", "/calendar", api_key, params=params
    )

@mcp.tool()
async def get_calendar_coverage(
    bloomberg_ticker: Optional[str] = None,
    isin: Optional[str] = None,
    cusip: Optional[str] = None,
    ric: Optional[str] = None,
    ticker: Optional[str] = None,
    permid: Optional[str] = None,
    watchlist_id: Optional[str] = None,
    company_rollup: Optional[bool] = None
) -> Dict[str, Any]:
    """Retrieve information about equities covered by the calendar API."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {}
    if bloomberg_ticker:
        params["bloomberg_ticker"] = bloomberg_ticker
    if isin:
        params["isin"] = isin
    if cusip:
        params["cusip"] = cusip
    if ric:
        params["ric"] = ric
    if ticker:
        params["ticker"] = ticker
    if permid:
        params["permid"] = permid
    if watchlist_id:
        params["watchlist_id"] = watchlist_id
    if company_rollup is not None:
        params["company_rollup"] = company_rollup
    
    return await make_aiera_request(
        client, "GET", "/calendar/coverage", api_key, params=params
    )

@mcp.tool()
async def get_calendar_event(event_id: str) -> Dict[str, Any]:
    """Retrieve details of a specific calendar event by ID."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    return await make_aiera_request(
        client, "GET", f"/calendar/{event_id}", api_key
    )

# Corporate Activity API Tools
@mcp.tool()
async def get_corporate_activity(
    bloomberg_ticker: str,
    start_date: str,
    end_date: str,
    activity_type: Optional[str] = None,
    activity_subtype: Optional[str] = None,
    modified_since: Optional[str] = None,
    from_index: Optional[int] = None,
    size: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve corporate activities with various filters."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {
        "bloomberg_ticker": bloomberg_ticker,
        "start_date": start_date,
        "end_date": end_date
    }
    
    if activity_type:
        params["activity_type"] = activity_type
    if activity_subtype:
        params["activity_subtype"] = activity_subtype
    if modified_since:
        params["modified_since"] = modified_since
    if from_index:
        params["from_index"] = from_index
    if size:
        params["size"] = size
    
    return await make_aiera_request(
        client, "GET", "/corporate-activity", api_key, params=params
    )

@mcp.tool()
async def get_corporate_activity_coverage(
    bloomberg_ticker: str,
    isin: Optional[str] = None,
    company_rollup: Optional[bool] = None,
    include_details: Optional[bool] = None
) -> Dict[str, Any]:
    """Retrieve details of equities covered by corporate activity API."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {"bloomberg_ticker": bloomberg_ticker}
    
    if isin:
        params["isin"] = isin
    if company_rollup is not None:
        params["company_rollup"] = company_rollup
    if include_details is not None:
        params["include_details"] = include_details
    
    return await make_aiera_request(
        client, "GET", "/corporate-activity/coverage", api_key, params=params
    )

@mcp.tool()
async def get_corporate_activity_by_id(
    corporate_activity_id: str,
    include_details: Optional[bool] = None
) -> Dict[str, Any]:
    """Fetch details of a specific corporate activity by ID."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {}
    if include_details is not None:
        params["include_details"] = include_details
    
    return await make_aiera_request(
        client, "GET", f"/corporate-activity/{corporate_activity_id}", api_key, params=params
    )

@mcp.tool()
async def get_corporate_activity_audits(
    bloomberg_ticker: str,
    start_date: str,
    end_date: str,
    size: int,
    from_index: int,
    modified_since: Optional[str] = None,
    isin: Optional[str] = None,
    cusip: Optional[str] = None,
    ric: Optional[str] = None,
    permid: Optional[str] = None,
    watchlist_id: Optional[str] = None,
    activity_type: Optional[str] = None,
    activity_subtype: Optional[str] = None,
    include_activity: Optional[bool] = None
) -> Dict[str, Any]:
    """Fetch audit logs for corporate activities."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {
        "bloomberg_ticker": bloomberg_ticker,
        "start_date": start_date,
        "end_date": end_date,
        "size": size,
        "from_index": from_index
    }
    
    if modified_since:
        params["modified_since"] = modified_since
    if isin:
        params["isin"] = isin
    if cusip:
        params["cusip"] = cusip
    if ric:
        params["ric"] = ric
    if permid:
        params["permid"] = permid
    if watchlist_id:
        params["watchlist_id"] = watchlist_id
    if activity_type:
        params["activity_type"] = activity_type
    if activity_subtype:
        params["activity_subtype"] = activity_subtype
    if include_activity is not None:
        params["include_activity"] = include_activity
    
    return await make_aiera_request(
        client, "GET", "/corporate-activity/audits", api_key, params=params
    )

# Content API Tools
@mcp.tool()
async def get_filings(
    bloomberg_ticker: str,
    start_date: str,
    end_date: str,
    form_number: Optional[str] = None,
    isin: Optional[str] = None,
    ric: Optional[str] = None,
    permid: Optional[str] = None,
    ticker: Optional[str] = None,
    from_id: Optional[str] = None,
    from_index: Optional[int] = None,
    size: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve filings content for specific equities with comprehensive filtering."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {
        "bloomberg_ticker": bloomberg_ticker,
        "start_date": start_date,
        "end_date": end_date
    }
    
    if form_number:
        params["form_number"] = form_number
    if isin:
        params["isin"] = isin
    if ric:
        params["ric"] = ric
    if permid:
        params["permid"] = permid
    if ticker:
        params["ticker"] = ticker
    if from_id:
        params["from_id"] = from_id
    if from_index:
        params["from_index"] = from_index
    if size:
        params["size"] = size
    
    return await make_aiera_request(
        client, "GET", "/content/filings", api_key, params=params
    )

@mcp.tool()
async def get_news(
    bloomberg_ticker: str,
    start_date: str,
    end_date: str,
    news_source_id: str,
    isin: Optional[str] = None,
    ric: Optional[str] = None,
    permid: Optional[str] = None,
    ticker: Optional[str] = None,
    from_id: Optional[str] = None,
    from_index: Optional[int] = None,
    size: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve news content for specific equities with comprehensive filtering."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {
        "bloomberg_ticker": bloomberg_ticker,
        "start_date": start_date,
        "end_date": end_date,
        "news_source_id": news_source_id
    }
    
    if isin:
        params["isin"] = isin
    if ric:
        params["ric"] = ric
    if permid:
        params["permid"] = permid
    if ticker:
        params["ticker"] = ticker
    if from_id:
        params["from_id"] = from_id
    if from_index:
        params["from_index"] = from_index
    if size:
        params["size"] = size
    
    return await make_aiera_request(
        client, "GET", "/content/news", api_key, params=params
    )

# Equity API Tools
@mcp.tool()
async def get_equity_sectors() -> Dict[str, Any]:
    """Retrieve sectors and subsectors."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    return await make_aiera_request(
        client, "GET", "/equities-v2/sectors", api_key
    )

@mcp.tool()
async def get_equities(
    bloomberg_ticker: Optional[str] = None,
    isin: Optional[str] = None,
    ric: Optional[str] = None,
    ticker: Optional[str] = None,
    permid: Optional[str] = None,
    sector_id: Optional[str] = None,
    subsector_id: Optional[str] = None,
    search: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    include_inactive: Optional[bool] = None,
    include_company_metadata: Optional[bool] = None
) -> Dict[str, Any]:
    """Retrieve a list of equities for the respective bloomberg ticker."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {}
    if bloomberg_ticker:
        params["bloomberg_ticker"] = bloomberg_ticker
    if isin:
        params["isin"] = isin
    if ric:
        params["ric"] = ric
    if ticker:
        params["ticker"] = ticker
    if permid:
        params["permid"] = permid
    if sector_id:
        params["sector_id"] = sector_id
    if subsector_id:
        params["subsector_id"] = subsector_id
    if search:
        params["search"] = search
    if page:
        params["page"] = page
    if page_size:
        params["page_size"] = page_size
    if include_inactive is not None:
        params["include_inactive"] = include_inactive
    if include_company_metadata is not None:
        params["include_company_metadata"] = include_company_metadata
    
    return await make_aiera_request(
        client, "GET", "/equities-v2", api_key, params=params
    )

@mcp.tool()
async def get_equity_by_id(
    equity_id: str,
    include_company_metadata: Optional[bool] = None
) -> Dict[str, Any]:
    """Retrieve equity information by equity ID."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {}
    if include_company_metadata is not None:
        params["include_company_metadata"] = include_company_metadata
    
    return await make_aiera_request(
        client, "GET", f"/equities-v2/{equity_id}", api_key, params=params
    )

@mcp.tool()
async def get_equity_summary(equity_id: str) -> Dict[str, Any]:
    """Retrieve detailed information about an equity including past and upcoming events."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    return await make_aiera_request(
        client, "GET", f"/equities-v2/{equity_id}/summary", api_key
    )

# Summaries API Tools
@mcp.tool()
async def get_event_summaries(
    bloomberg_ticker: str,
    start_date: str,
    end_date: str,
    event_type: Optional[str] = None,
    isin: Optional[str] = None,
    ric: Optional[str] = None,
    permid: Optional[str] = None,
    summary_type: Optional[str] = "zeroshot",
    version: Optional[str] = None,
    from_index: Optional[int] = None,
    size: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve summaries based on filters like bloomberg ticker, start date and end date."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {
        "bloomberg_ticker": bloomberg_ticker,
        "start_date": start_date,
        "end_date": end_date
    }
    
    if event_type:
        params["event_type"] = event_type
    if isin:
        params["isin"] = isin
    if ric:
        params["ric"] = ric
    if permid:
        params["permid"] = permid
    if summary_type:
        params["summary_type"] = summary_type
    if version:
        params["version"] = version
    if from_index:
        params["from_index"] = from_index
    if size:
        params["size"] = size
    
    return await make_aiera_request(
        client, "GET", "/summaries", api_key, params=params
    )

@mcp.tool()
async def get_event_summary(event_id: str) -> Dict[str, Any]:
    """Retrieve a summary for a specific event ID."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    return await make_aiera_request(
        client, "GET", f"/summaries/{event_id}", api_key
    )

@mcp.tool()
async def get_event_summary_by_type(event_id: str, summary_type: str) -> Dict[str, Any]:
    """Retrieve a summary for a specific event ID and summary type."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    return await make_aiera_request(
        client, "GET", f"/summaries/{event_id}/{summary_type}", api_key
    )

# Topics API Tools
@mcp.tool()
async def get_topic_by_id(
    topic_id: str,
    include_metrics: Optional[bool] = None
) -> Dict[str, Any]:
    """Retrieve topic by topic ID."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {}
    if include_metrics is not None:
        params["include_metrics"] = include_metrics
    
    return await make_aiera_request(
        client, "GET", f"/topics/{topic_id}", api_key, params=params
    )

@mcp.tool()
async def get_topics(
    search: str,
    size: Optional[int] = None,
    from_index: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve a list of topics that match the parameters provided."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {"search": search}
    if size:
        params["size"] = size
    if from_index:
        params["from_index"] = from_index
    
    return await make_aiera_request(
        client, "GET", "/topics", api_key, params=params
    )

@mcp.tool()
async def get_topics_with_equities(
    search: str,
    size: Optional[int] = None,
    from_index: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve a list of topics and equities that match the parameters provided."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {"search": search}
    if size:
        params["size"] = size
    if from_index:
        params["from_index"] = from_index
    
    return await make_aiera_request(
        client, "GET", "/topics/from_equities", api_key, params=params
    )

@mcp.tool()
async def get_topics_with_events(
    search: str,
    size: Optional[int] = None,
    from_index: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve a list of topics and event counts that match the parameters provided."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {"search": search}
    if size:
        params["size"] = size
    if from_index:
        params["from_index"] = from_index
    
    return await make_aiera_request(
        client, "GET", "/topics/from_events", api_key, params=params
    )

@mcp.tool()
async def get_topic_equities(
    topic_id: str,
    size: Optional[int] = None,
    from_index: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve equities for a specific topic."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {}
    if size:
        params["size"] = size
    if from_index:
        params["from_index"] = from_index
    
    return await make_aiera_request(
        client, "GET", f"/topics/{topic_id}/equities", api_key, params=params
    )

@mcp.tool()
async def get_topic_events(
    topic_id: str,
    size: Optional[int] = None,
    from_index: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve events for a specific topic."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {}
    if size:
        params["size"] = size
    if from_index:
        params["from_index"] = from_index
    
    return await make_aiera_request(
        client, "GET", f"/topics/{topic_id}/events", api_key, params=params
    )

# Speaker API Tools
@mcp.tool()
async def get_person_info(person_id: str) -> Dict[str, Any]:
    """Retrieve information about a speaker's name, titles, and events."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    return await make_aiera_request(
        client, "GET", f"/events-v2/person/{person_id}", api_key
    )

# Monitor API Tools
@mcp.tool()
async def get_dashboard_stream_matches(
    dashboard_guid: str,
    stream_guid: str,
    start_date: str,
    end_date: str,
    linguistics: Optional[bool] = None,
    collapse: Optional[bool] = None,
    collapse_size: Optional[int] = None,
    next_page_token: Optional[str] = None,
    from_index: Optional[int] = None,
    size: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve stream matches from a monitor configured in Aiera desktop."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    
    if linguistics is not None:
        params["linguistics"] = linguistics
    if collapse is not None:
        params["collapse"] = collapse
    if collapse_size:
        params["collapse_size"] = collapse_size
    if next_page_token:
        params["next_page_token"] = next_page_token
    if from_index:
        params["from_index"] = from_index
    if size:
        params["size"] = size
    
    return await make_aiera_request(
        client, "GET", f"/dashboards/{dashboard_guid}/streams/{stream_guid}/matches", 
        api_key, params=params
    )

# Tonal Sentiments API Tools
@mcp.tool()
async def get_tonal_sentiments(
    bloomberg_ticker: Optional[str] = None
) -> str:
    """Export tonal sentiment data to CSV format."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {}
    if bloomberg_ticker:
        params["bloomberg_ticker"] = bloomberg_ticker
    
    headers = DEFAULT_HEADERS.copy()
    headers["X-API-KEY"] = api_key
    
    response = await client.get(
        f"{AIERA_BASE_URL}/events-v2/tonal/export/csv",
        params=params,
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve tonal sentiments: {response.status_code}")
    
    return response.text

# Transcrippets API Tools
@mcp.tool()
async def get_transcrippets(
    transcrippet_id: Optional[str] = None,
    event_id: Optional[str] = None,
    equity_id: Optional[str] = None,
    speaker_id: Optional[str] = None,
    transcript_item_id: Optional[str] = None,
    created_start_date: Optional[str] = None,
    created_end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Retrieve transcrippet URLs and metadata."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")
    
    params = {}
    if transcrippet_id:
        params["transcrippet_id"] = transcrippet_id
    if event_id:
        params["event_id"] = event_id
    if equity_id:
        params["equity_id"] = equity_id
    if speaker_id:
        params["speaker_id"] = speaker_id
    if transcript_item_id:
        params["transcript_item_id"] = transcript_item_id
    if created_start_date:
        params["created_start_date"] = created_start_date
    if created_end_date:
        params["created_end_date"] = created_end_date
    
    return await make_aiera_request(
        client, "GET", "/transcrippets", api_key, params=params
    )

# Resources for API documentation
@mcp.resource("aiera://api/docs")
def get_api_documentation() -> str:
    """Provide documentation for the Aiera API."""
    return """
    # Aiera Financial Data API
    
    This MCP server provides access to Aiera's comprehensive financial data API.
    
    ## Available Tools:
    
    ### Events API
    - get_event_transcripts: Retrieve CSV transcripts for events
    - get_event: Get a single event by ID with optional pricing/linguistics
    - get_events: Get events with filtering by ticker, date range, event type
    
    ### Calendar API
    - get_calendar: Fetch calendar events with comprehensive filtering
    - get_calendar_coverage: Get information about covered equities
    - get_calendar_event: Get specific calendar event details by ID
    
    ### Corporate Activity API  
    - get_corporate_activity: Retrieve corporate activities with filters
    - get_corporate_activity_coverage: Get coverage information for corporate activities
    - get_corporate_activity_by_id: Get specific corporate activity by ID
    - get_corporate_activity_audits: Get audit logs for corporate activities
    
    ### Content API
    - get_filings: Retrieve SEC filings with comprehensive filtering
    - get_news: Get news content with source and date filtering
    
    ### Equity API
    - get_equity_sectors: Get available sectors and subsectors
    - get_equities: List equities with advanced filtering options
    - get_equity_by_id: Get equity by ID with optional company metadata
    - get_equity_summary: Get detailed equity information with events
    
    ### Summaries API
    - get_event_summaries: Get event summaries with filtering
    - get_event_summary: Get summary for specific event
    - get_event_summary_by_type: Get typed summary for event
    
    ### Topics API
    - get_topic_by_id: Get individual topic details with metrics
    - get_topics: List topics with search functionality
    - get_topics_with_equities: Get topics with equity information
    - get_topics_with_events: Get topics with event counts
    - get_topic_equities: Get equities for a specific topic
    - get_topic_events: Get events for a specific topic
    
    ### Speaker API
    - get_person_info: Get speaker information by person ID
    
    ### Monitor API
    - get_dashboard_stream_matches: Get dashboard stream matches with advanced filtering
    
    ### Tonal Sentiments API
    - get_tonal_sentiments: Export tonal sentiment data to CSV
    
    ### Transcrippets API
    - get_transcrippets: Retrieve transcrippet URLs and metadata
    
    ## Authentication:
    All endpoints require the AIERA_API_KEY environment variable to be set.
    
    ## Parameter Notes:
    - Most endpoints support pagination using 'size' and 'from_index' parameters
    - Date parameters should be in ISO format (YYYY-MM-DD)
    - Bloomberg tickers should include country code (e.g., "AAPL:US")
    - Boolean parameters accept true/false values
    """

if __name__ == "__main__":
    # For local testing
    mcp.run(transport="streamable-http")