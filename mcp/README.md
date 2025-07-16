# Aiera MCP Server

A Model Context Protocol (MCP) server for accessing Aiera's financial data API, designed for deployment on AWS Lambda.

## Overview

This MCP server provides a standardized interface for AI applications to access Aiera's comprehensive financial data, including:

- **Events**: Earnings calls, conferences, and other financial events with transcripts
- **Calendar**: Upcoming financial events and earnings dates with coverage information
- **Corporate Activity**: M&A, spin-offs, and other corporate activities with audit trails
- **Content**: SEC filings, news articles, and press releases with advanced filtering
- **Equity**: Stock information, company data, sectors, and detailed summaries
- **Summaries**: AI-generated summaries of financial events with multiple types
- **Topics**: Categorized financial topics and themes with equity/event associations
- **Speakers**: Information about executives and speakers from events
- **Monitor**: Dashboard stream matches and alerts with advanced filtering
- **Tonal Sentiments**: Sentiment analysis data export capabilities
- **Transcrippets**: Transcript snippets and metadata access

## Features

- **Serverless Deployment**: Optimized for AWS Lambda with stateless HTTP transport
- **Authentication**: Secure API key authentication following Aiera's requirements
- **Comprehensive Coverage**: All 32 tools covering 12 API categories across all OpenAPI specifications
- **Type Safety**: Full type annotations and structured responses
- **Error Handling**: Robust error handling and validation
- **Advanced Parameters**: Full parameter support matching OpenAPI specifications
- **Documentation**: Built-in API documentation and help resources
- **Scalable**: Auto-scaling Lambda deployment with CloudFormation

## Quick Start

### Prerequisites

- Python 3.11 or higher
- AWS CLI configured with appropriate permissions
- SAM CLI installed
- Aiera API key

### Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
```bash
export AIERA_API_KEY="your-aiera-api-key"
```

3. **Test locally**:
```bash
python test_local.py
```

4. **Run server locally**:
```bash
python server.py
```

### Deployment to AWS Lambda

1. **Deploy using the provided script**:
```bash
./deploy.sh
```

2. **Deploy to specific stage**:
```bash
./deploy.sh -s prod -r us-west-2
```

3. **Deploy with custom S3 bucket**:
```bash
./deploy.sh -b my-custom-bucket
```

## API Reference

### Authentication

All requests require the `AIERA_API_KEY` environment variable to be set. The server handles authentication automatically using Aiera's X-API-KEY header system.

### Available Tools

#### Events API
- `get_events(bloomberg_ticker, start_date, end_date, event_type?, modified_since?)` - Get financial events
- `get_event(event_id, pricing?, linguistics?)` - Get specific event details with optional pricing/linguistics
- `get_event_transcripts(event_ids)` - Get event transcripts in CSV format

#### Calendar API
- `get_calendar(bloomberg_ticker?, start_date?, end_date?, event_type?, modified_since?, from_index?, size?, sort_key?)` - Get calendar events
- `get_calendar_coverage(bloomberg_ticker?, isin?, cusip?, ric?, ticker?, permid?, watchlist_id?, company_rollup?)` - Get calendar coverage information
- `get_calendar_event(event_id)` - Get specific calendar event details

#### Corporate Activity API
- `get_corporate_activity(bloomberg_ticker, start_date, end_date, activity_type?, activity_subtype?, modified_since?, from_index?, size?)` - Get corporate activities
- `get_corporate_activity_coverage(bloomberg_ticker, isin?, company_rollup?, include_details?)` - Get corporate activity coverage
- `get_corporate_activity_by_id(corporate_activity_id, include_details?)` - Get specific corporate activity
- `get_corporate_activity_audits(bloomberg_ticker, start_date, end_date, size, from_index, ...)` - Get corporate activity audits

#### Content API
- `get_filings(bloomberg_ticker, start_date, end_date, form_number?, isin?, ric?, permid?, ticker?, from_id?, from_index?, size?)` - Get SEC filings
- `get_news(bloomberg_ticker, start_date, end_date, news_source_id, isin?, ric?, permid?, ticker?, from_id?, from_index?, size?)` - Get news articles

#### Equity API
- `get_equity_sectors()` - Get available sectors and subsectors
- `get_equities(bloomberg_ticker?, isin?, ric?, ticker?, permid?, sector_id?, subsector_id?, search?, page?, page_size?, include_inactive?, include_company_metadata?)` - Get equity information
- `get_equity_by_id(equity_id, include_company_metadata?)` - Get specific equity details
- `get_equity_summary(equity_id)` - Get detailed equity information with events

#### Summaries API
- `get_event_summaries(bloomberg_ticker, start_date, end_date, event_type?, isin?, ric?, permid?, summary_type?, version?, from_index?, size?)` - Get event summaries
- `get_event_summary(event_id)` - Get specific event summary
- `get_event_summary_by_type(event_id, summary_type)` - Get typed event summary

#### Topics API
- `get_topic_by_id(topic_id, include_metrics?)` - Get individual topic details
- `get_topics(search, size?, from_index?)` - Get financial topics
- `get_topics_with_equities(search, size?, from_index?)` - Get topics with equity information
- `get_topics_with_events(search, size?, from_index?)` - Get topics with event counts
- `get_topic_equities(topic_id, size?, from_index?)` - Get equities for a topic
- `get_topic_events(topic_id, size?, from_index?)` - Get events for a topic

#### Speaker API
- `get_person_info(person_id)` - Get speaker information

#### Monitor API
- `get_dashboard_stream_matches(dashboard_guid, stream_guid, start_date, end_date, linguistics?, collapse?, collapse_size?, next_page_token?, from_index?, size?)` - Get dashboard matches

#### Tonal Sentiments API
- `get_tonal_sentiments(bloomberg_ticker?)` - Export tonal sentiment data to CSV

#### Transcrippets API
- `get_transcrippets(transcrippet_id?, event_id?, equity_id?, speaker_id?, transcript_item_id?, created_start_date?, created_end_date?)` - Get transcrippet URLs and metadata

### Resources

- `aiera://api/docs` - API documentation and help

## Configuration

### Environment Variables

- `AIERA_API_KEY` (required) - Your Aiera API key
- `STAGE` (optional) - Deployment stage (dev, staging, prod)

### AWS Lambda Configuration

- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Architecture**: x86_64

## Development

### Project Structure

```
mcp/
├── server.py              # Main MCP server implementation
├── lambda_handler.py      # AWS Lambda handler
├── template.yaml          # SAM CloudFormation template
├── deploy.sh             # Deployment script
├── test_local.py         # Local testing script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Adding New Tools

1. **Define the tool function** in `server.py`:
```python
@mcp.tool()
async def new_tool(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """Tool description."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")
    
    return await make_aiera_request(
        client, "GET", f"/new/endpoint/{param1}", api_key, 
        params={"param2": param2} if param2 else None
    )
```

2. **Test locally**:
```bash
python test_local.py
```

3. **Deploy**:
```bash
./deploy.sh
```

### Local Development

1. **Start the server**:
```bash
python server.py
```

2. **Test with curl**:
```bash
curl -X POST http://localhost:3000/sse \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "get_events"}}'
```

## Deployment Options

### Development
```bash
./deploy.sh -s dev
```

### Staging
```bash
./deploy.sh -s staging
```

### Production
```bash
./deploy.sh -s prod
```

### Custom Region
```bash
./deploy.sh -r us-west-2
```

## Monitoring and Logging

The server includes comprehensive logging through CloudWatch:

- **Lambda Logs**: `/aws/lambda/aiera-mcp-server-{stage}`
- **API Gateway Logs**: Configured for error tracking
- **Retention**: 14 days (configurable in template.yaml)

## Security

- **API Key Protection**: Aiera API key is stored as environment variable
- **HTTPS Only**: All communications encrypted in transit
- **IAM Roles**: Minimal permissions for Lambda execution
- **Input Validation**: All parameters validated before API calls

## Troubleshooting

### Common Issues

1. **API Key Not Set**:
   - Ensure `AIERA_API_KEY` environment variable is set
   - Check CloudFormation parameters

2. **Deployment Fails**:
   - Verify AWS credentials: `aws sts get-caller-identity`
   - Check SAM CLI installation: `sam --version`

3. **Lambda Timeout**:
   - Increase timeout in `template.yaml`
   - Monitor CloudWatch logs for specific errors

4. **API Gateway Errors**:
   - Check API Gateway logs in CloudWatch
   - Verify CORS configuration

### Debugging

1. **Check Lambda logs**:
```bash
aws logs tail /aws/lambda/aiera-mcp-server-dev --follow
```

2. **Test Lambda function directly**:
```bash
aws lambda invoke --function-name aiera-mcp-server-dev response.json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run local tests: `python test_local.py`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues related to:
- **MCP Server**: Open an issue in this repository
- **Aiera API**: Contact Aiera support at support@aiera.com
- **AWS Deployment**: Check AWS documentation and CloudFormation logs