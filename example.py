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
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate

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
        name="Corporate Activities API",
        func=planner.create_openapi_agent(corporate_activities_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to retrieve a list of corporate activities that match the parameters provided or the corporate activity id and return the list of events directly, the corporate activity coverage, and to retrive the audits for them. When asked about counts or numbers or how many, return only the the count of results, formatted as a number "
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
        1. ONE API CALL ONLY PER REQUEST - NO EXCEPTIONS
        
        Allowed Operations (Choose Only One):
        - ONE GET /topics with search parameter
        - ONE GET /topics (no parameters)
        - ONE GET /topics/topic_id
        - ONE GET /topics/topic_id/equities
        - ONE GET /topics/topic_id/events
        - ONE GET /topics/from_equities
        - ONE GET /topics/from_events
        
        Usage Patterns:
        1. Search topics by word:
           - Use: GET /topics?search=word
           - Return: Only topic names and IDs
           - STOP immediately after
        
        2. Get all topics:
           - Use: GET /topics
           - Return: Only topic names and IDs
           - STOP immediately after
        
        3. Get topic by ID:
           - Use: GET /topics/topic_id
           - Return: Only requested topic info
           - STOP immediately after
        
        4. Get equities/events for topic ID:
           - Use: Either /topics/topic_id/equities OR /topics/topic_id/events
           - Return: Only requested association info
           - STOP immediately after
        
        FORBIDDEN:
        - Multiple API calls
        - Chaining requests
        - Following up with additional queries"""
    )

    equities_tool=Tool(
        name="Equities API",
        func=planner.create_openapi_agent(equities_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description=" Tool to retrieve a list of sectors along with their subsectors, to retrieve a list of equities and to retrive equity info according to the equity id. When asked about info on sectors/ subsectors, call the /equities-v2/sectors and the output returned should be displayed as pointers and NOT as an error.STOP IMMEDIATELY "
    )

    contents_tool=Tool(
        name="Contents API",
        func= planner.create_openapi_agent(contents_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description= "Tool to retrieve filings and news content for specific equities or filters such as form number, date range, or ticker symbol. All the details should be displayed in the ouput result."
    )

    transcrippets_tool=Tool(
        name="Trabscrippets API",
        func=planner.create_openapi_agent(transcrippets_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to retrieve a transcrippet url according to the parameters"
    )

    tonalSentiment_tool=Tool(
        name="Tonal Sentiment API",
        func=planner.create_openapi_agent(tonalSentiment_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to Export tonal sentiment to csv."
    )

    summaries_tool= Tool(
        name="Summaries API",
        func=planner.create_openapi_agent(summaries_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool for retrieving the field summaries from events. Use this only when specifically asked for summaries based on event filter, event_id, and summary_type. When asked to get summaries for a specific bloomberg ticker within a given date range call /summaries with the parameters as enetered by the user"
    )

    return[events_tool, calendars_tool, speaker_tool, corporate_activities_tool, monitors_tool, topics_tool, equities_tool, contents_tool, transcrippets_tool, tonalSentiment_tool, summaries_tool]


def create_openapi_agent():
    tools = create_openapi_tools()
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.3, max_tokens=10000)
    system_message = """You are an AI assistant with access to various API tools. When given an input you need to choose from the various tools:
    1. Events API: Tool to get Event Transcripts as a csv file,  retrieve an event using an event id, or to get a list of events that match the parameters provided
    2. Calendars API: Tool to get a list of calendar events filtered by equity, watchlist, or other parameters, to retrieve information about equities covered by the API and to retrieve details of a specific calendar event by its event ID
    3. Speakers API: Tool to retrieves a person's information using their person id.
    4. Corporate Activities API: Tool to retrieve a list of corporate activities that match the parameters provided or the corporate activity id, the corporate activity coverage, and to retrieve the audits for them. If asked to get the audit details call the GET /corporate-activity/audits api.  When asked about counts or numbers, return only the the count of results, formatted as a number
    5. Monitors API: Tool to retrieve a stream match using a dashboard guid and stream guid
    6. Topics API: Tool to retrieve info regarding topics, retrieving number of equities or events related to a specific topic according to the search term/ word.
    7. Equities API: Tool to retrieve a list of sectors along with their subsectors, to retrieve a list of equities and to retrive equity info according to the equity id or bloomberg ticker. 
    8. Contents API: Tool to retrieve filings and news content for specific equities or filters such as form number, date range, or ticker symbol
    9. Transcrippets API: Tool to retrieve a transcrippet url according to the parameters
    10. Tonal Sentiment API: Tool to retrieve a csv file of the tonal sentiments.
    11. Summaries API: Tool for retrieving the summaries attribute of an event. Use this only when specifically asked for summaries based on event filter, event_id, and summary_type. When asked to get summaries for a specific bloomberg ticker within a given date range call /summaries with the parameters as enetered by the user
    Follow these strict guidelines:
    For topic searches:

    1. IF the query contains "get topics" or "find topics" or "search topics":
       - ONLY use GET /topics?search=word
       - Return EXACT response
       - STOP IMMEDIATELY
   2. IF the query contains "how many equities for topics related to XYZ":
       - ONLY use GET /topics/from_equities and replace search=XYZ
       - DO NOT use XYZ as a topic id
   3. IF the query contains "how many events for topics related to XYZ":
       - ONLY use GET /topics/from_events and replace search=XYZ
       - DO NOT use XYZ as a topic id
 
    


    For equities-v2 searches:
    1. IF the query contains "Get equity info for XYZ":
      - ONLY use GET /equities-v2?bloomberg_ticker=XYZ
      - DO NOT USE this if a particular topic is mentioned

    
    For corporate audit searches:
    1. IF the query contains "get audit details" or "find audit details":
       - ONLY use GET /corporate-activity/audits 
       
    CRITICAL RULES:
    1. ONE API CALL ONLY - You must stop after making a single API call
    2. NO FOLLOW-UP CALLS - Never attempt additional queries
    3. NO CHAINING - Do not try to combine multiple endpoints
    Process:
    1. Analyze the user query carefully
    2. Identify the SINGLE most appropriate API endpoint
    3. Make ONE call only
    4. Return results immediately
    5. STOP COMPLETELY - Do not attempt any additional operations
    
    1. Single API Call Rule (MOST IMPORTANT):
       - You MUST make exactly ONE API call per request
       - NEVER make follow-up API calls
    
    3. API Usage Rules:
       - Always check if the required information can be obtained from a single API call
       - Do not make exploratory API calls - only call what's necessary
       - When searching, use the most specific parameters available
       - If an API call fails, explain the issue rather than trying alternative calls
    
    4. Response Guidelines:
       - Provide direct, concise responses
       - Only include information specifically requested
       - Format responses clearly and consistently
       - If the required information cannot be obtained with a single API call, explain why

    5. Error Handling:
       - If an API call fails, do not attempt multiple alternative calls
       - Clearly report any errors or limitations
       - Suggest the most appropriate alternative approach if needed
    Important Example: When asked to retrive the topics with the word "covid" in it, you should use the /topics?search=covid endpoint and stop immediately. If asked to find the events associated with a topic id, you should use the /topics/topic_id/events endpoint and stop immediately. If asked to find the equities associated with a topic id, you should use the /topics/topic_id/equities endpoint and stop immediately. If asked to find the events for a topic related to a word, DO NOT fetch the topic id but you should use the /topics/from_events endpoint with search=word and stop immediately. If asked to find the equities for a topic related to a word, DO NOT fetch the topic id you should use the /topics/from_equities endpoint with search=word and stop immediately.
    Remember: Your goal is to be efficient and precise, using only and only 1 API calls while providing accurate information
     You MUST STOP after the first API call, regardless of the results.
    CRITICAL: You must STOP after the first agent run. Do not make any additional calls regardless of the data received.
     YOU MUST USE THE .TXT FILE ONLY FOR THE SPEAKER DETAILS
    """


    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_message),
    ])
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        prompt=prompt,
        agent_type=AgentType.OPENAI_FUNCTIONS,  
        verbose=True,
        max_iterations=100,
        early_stopping_method="force",
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

