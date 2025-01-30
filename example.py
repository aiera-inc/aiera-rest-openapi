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

    events_tool = Tool(
        name= "Events API",
        func=planner.create_openapi_agent(events_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to get Event Transcripts as a csv file,  retrieve an event using an event id, or to get a list of events that match the parameters provided"
    )


    speaker_tool= Tool(
        name="Speakers API",
        func=planner.create_openapi_agent(speaker_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to retrieve retrieves a person's information using their person id."
    )

    summaries_tool= Tool(
        name="Summaries API",
        func=planner.create_openapi_agent(summaries_api_spec, requests_wrapper, llm, allow_dangerous_requests=True).invoke,
        description="Tool to retrieve summaries based on the events filter, event_id, and summary_type."
    )


    return[events_tool, speaker_tool]


def create_openapi_agent():
    tools = create_openapi_tools()
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.3)
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.OPENAI_FUNCTIONS,  # Correct parameter name
        verbose=True,
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

