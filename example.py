from langchain_community.agent_toolkits.openapi import planner
from langchain_openai import ChatOpenAI
import yaml
import os
from langchain_community.utilities.requests import RequestsWrapper
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain.callbacks.tracers import ConsoleCallbackHandler



def construct_aiera_auth_headers():
    return {"X-API-Key": os.environ["AIERA_API_KEY"]}


headers = construct_aiera_auth_headers()
requests_wrapper = RequestsWrapper(headers=headers)


llm = ChatOpenAI(model_name="gpt-4", temperature=0.3)

# Load the API spec from the YAML file
with open("specs/events.yaml", "r") as file:
    raw_events_api_spec = yaml.safe_load(file)

events_api_spec = reduce_openapi_spec(raw_events_api_spec)

# NOTE: set allow_dangerous_requests manually for security concern https://python.langchain.com/docs/security
agent = planner.create_openapi_agent(
    events_api_spec,
    requests_wrapper,
    llm,
    allow_dangerous_requests=True,
)

# Example: Retrieve events based on a start and end date
query = """
Fetch events for the Bloomberg ticker 'AAPL:US' from '2023-09-01' to '2023-09-15'.
"""

# Run the agent with the query
response = agent.invoke(query, config={'callbacks': [ConsoleCallbackHandler()]})

print(response)