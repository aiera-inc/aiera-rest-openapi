import streamlit as st
from langchain_community.agent_toolkits.openapi import planner
from langchain_openai import ChatOpenAI
import yaml
import os
from langchain.agents import AgentType
from langchain_community.utilities.requests import RequestsWrapper
from langchain.tools import Tool
from langchain.agents import AgentType
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.agents import initialize_agent 
import re

# Construct authentication headers
def construct_aiera_auth_headers():
    return {"X-API-Key": os.environ["AIERA_API_KEY"]}

# Load OpenAPI spec
def load_openapi_spec(file_path):
    with open(file_path, "r") as file:
        raw_spec = yaml.safe_load(file)
    return reduce_openapi_spec(raw_spec)


# Create agent
def create_openapi_tools():
    headers = construct_aiera_auth_headers()
    requests_wrapper = RequestsWrapper(headers=headers)
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.3)  

    events_api_spec = load_openapi_spec("specs/events.yaml")
    speaker_api_spec = load_openapi_spec("specs/speaker.yaml")
    summaries_api_spec = load_openapi_spec("specs/summaries.yaml")
    corporate_activities_api_spec=load_openapi_spec('specs/corporate_activity.yaml')
    monitors_api_spec=load_openapi_spec('specs/monitor.yaml')
    topics_api_spec=load_openapi_spec('specs/topics.yaml')
    equities_api_spec=load_openapi_spec('specs/equity.yaml')
    contents_api_spec=load_openapi_spec('specs/content.yaml')
    transcrippets_api_spec=load_openapi_spec('specs/transcrippets.yaml')
    tonalSentiment_api_spec=load_openapi_spec('specs/tonalSentiments.yaml')
    calendar_api_spec=load_openapi_spec('specs/calendar.yaml')

    events_tool = Tool(
        name= "Events API",
        func=planner.create_openapi_agent(events_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to get Event Transcripts as a csv file,  retrieve an event using an event id, or to get a list of events that match the parameters provided"
    )

    calendars_tool= Tool(
        name= "Calendars API",
        func=planner.create_openapi_agent(calendar_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to get a list of calendar events filtered by equity, watchlist, or other parameters, to retrieve information about equities covered by the API and to retrieve details of a specific calendar event by its event ID "
    )


    speaker_tool= Tool(
        name="Speakers API",
        func=planner.create_openapi_agent(speaker_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to retrieves a person's information using their person id."
    )

    corporate_activities_tool= Tool(
        name="Cporporate Activities API",
        func=planner.create_openapi_agent(corporate_activities_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to retrieve a list of corporate activities that match the parameters provided or the corporate activity id, the corporate activity coverage, and to retrive the audits for them. When asked about counts or numbers, return only the the count of results, formatted as a number "
    )

    monitors_tool= Tool(
        name="Monitors API",
        func=planner.create_openapi_agent(monitors_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to retrieve a stream match using a dashboard guid and stream guid "
    )

    topics_tool=Tool(
        name="Topics API",
        func=planner.create_openapi_agent(topics_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="""Tool to retrieve list of topics. IMPORTANT RULES:
    1. When searching for topics containing a specific word:
       - ONLY call GET /topics
       - Return ONLY the direct response
       - DO NOT fetch any additional information
       - DO NOT call any other endpoints
       - STOP after getting the topics list
    
    2. When retrieving all topics:
       - Call GET /topics
       - Return ONLY topic names and IDs
       - STOP after getting the list
    
    3. For specific topic ID requests:
       - Use GET /topics/topic_id
    
    4. For topic-related equities or events:
       - With topic ID: Use /topics/topic_id/equities or /topics/topic_id/events
       - Without topic ID: Use /topics/equities or /topics/events
    
    IMPORTANT: When asked about topics containing a word (e.g., 'covid'), ONLY use GET /topics?query=word and return the direct response. DO NOT fetch additional details."""
    )

    equities_tool=Tool(
        name="Equities API",
        func=planner.create_openapi_agent(equities_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description=" Tool to retrieve a list of sectors along with their subsectors, to retrieve a list of equities and to retrive equity info according to the equity id "
    )

    contents_tool=Tool(
        name="Contents API",
        func= planner.create_openapi_agent(contents_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description= "Tool to retrieve filings and news content for specific equities or filters such as form number, date range, or ticker symbol"
    )

    transcrippeets_tool=Tool(
        name="Trabscrippets API",
        func=planner.create_openapi_agent(transcrippets_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to retrieve a transcrippet url according to the parameters"
    )

    tonalSentiment_tool=Tool(
        name="Tonal Sentiment API",
        func=planner.create_openapi_agent(tonalSentiment_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to retrieve a csv file of the tonal sentiments."
    )

    summaries_tool= Tool(
        name="Summaries API",
        func=planner.create_openapi_agent(summaries_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool for retrieving the field summaries from events. Use this only when specifically asked for summaries based on event filter, event_id, and summary_type."
    )

    return[events_tool, calendars_tool, speaker_tool, summaries_tool, corporate_activities_tool, monitors_tool, topics_tool, equities_tool, contents_tool, transcrippeets_tool, tonalSentiment_tool]


def create_openapi_agent():
    tools = create_openapi_tools()
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.3, max_tokens=1000)
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.OPENAI_FUNCTIONS,  # Correct parameter name
        verbose=True,
        max_iterations=10000,
        max_execution_time=120,
        handle_parsing_errors=True
    )
    return agent


# Function to handle user queries and agent responses
def get_chat_response(query):
    agent = create_openapi_agent()
    response = agent.invoke(query, config={'callbacks': [ConsoleCallbackHandler()]})
    return response

# Set up Streamlit page
st.set_page_config(page_title="Chat Application", page_icon="💬", layout="centered")

st.title("💬 GPT-4 Chat Application")
st.write("Chat with GPT-4 using Langchain, OpenAI, and Aiera.")

# Initialize session state for storing chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "input" not in st.session_state:
    st.session_state.input = "" 

# Function to display the chat history
def display_chat():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.write(f"**You**: {msg['content']}")
        else:
            st.write(f"**Assistant**: {msg['content']}")


# Display the chat history
#if st.session_state.messages:
#    display_chat()



# container for chat history
response_container = st.container()

# container for text input
container = st.container()


with container:
    with st.form(key='user_input_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')
    
        # if user has submitted input, submit and process messages
        if submit_button and user_input: 

            with st.spinner(text='Processing...'):

                st.session_state.messages.append({"role": "user", "content": user_input})

                response = get_chat_response(st.session_state.input)

                # update messages
                st.session_state.messages.append({"role": "assistant", "content": response["output"]})


    
if st.session_state.messages:

    with response_container:
        citations = []
        for i, mess in enumerate(st.session_state.messages):

            if mess["role"] == "user":
                with st.chat_message('You', avatar="user"):
                    st.write(mess["content"])

            else:
                content = mess["content"]
                if "【" in content:
                    content = re.sub(r'【(.*?)】', '', content)

                with st.chat_message('Aiera', avatar="assistant"):
                # avatar=f"{ROOT_DIR}/aiera_assistant/assets/aiera-icon-logo-circle.png"):
                    st.write(content)

