# Aiera OpenAPI Specifications
This repository contains OpenAPI specifications for Aiera's REST endpoint, designed to facilitate integration with function calling models on OpenAI.

## Overview
Aiera provides a powerful REST API that allows developers to access financial data, earnings call transcripts, and other valuable information. This OpenAPI specification enables seamless integration with OpenAI's function calling models, enhancing the capabilities of AI-powered financial analysis tools.

## Key Features

* OpenAI Function Calling Compatibility: Structured in a way that's optimized for use with OpenAI's function calling feature.
* Easy Integration: Can be used with popular OpenAPI tools and code generators for quick implementation in various programming languages.

## Usage

1. Clone this repository to your local machine.
2. Use the appropriate yaml file with your preferred OpenAPI tools or SDKs.
3. Integrate the specified endpoints with your OpenAI function calling implementations.

## Example

This repo is packaged with an example found in `example.py`. To use the example, create a conda environment:

```bash
conda env create -f environment.yml
conda activate aiera-rest-openapi
```

Set your environment variables to use the OpenAI client and Aiera endpoint:
```bash
export OPENAI_API_KEY=...
export OPENAI_ORG_ID=...
export AIERA_API_KEY=...
```

Now, you can run the script:
```bash
python example.py
```


## Endpoints
The specification includes the following key endpoints:

* /events: Retrieve information about events.

## Authentication
To use the Aiera API, you'll need to obtain an API key. For more information about Aiera and its services, visit www.aiera.com.
## Support
For questions or issues related to the OpenAPI specification, please open an issue in this repository. For general API support or account-related queries, please contact Aiera support.
## License
This OpenAPI specification is provided under the MIT License.

For more information about Aiera and its services, visit www.aiera.com.