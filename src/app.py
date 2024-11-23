import streamlit as st
import streamlit.components.v1 as components
import logging
import yaml
import random
import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
from service.ai_service import AIAssistantManager
from service.run import StreamlitEventHandler
from styles import get_page_styling, get_particles_js, AVATAR_URLS

SETUP = 'interface'

# Welcome messages list
WELCOME_MESSAGES = [
    "Welcome to the Snack Brands Australia Performance Hub! Here, you can explore detailed insights into your operational KPIs, assess plant performance, and find opportunities to enhance efficiency. Let's dive into the data and boost your production success!",
    "Hello and welcome! You've accessed Snack Brands Australia's comprehensive tool for optimizing plant operations. Whether you're looking to analyze KPIs, forecast scenarios, or improve processes, we've got the data-driven insights you need. Let's get started!",
    "Welcome to Snack Brands Australia's Operational Dashboard! Discover the power of data as you navigate through KPIs, track plant performance, and make informed decisions to optimize your operations. Ready to elevate your efficiency?",
    "Greetings! At Snack Brands Australia, understanding your operational metrics is key to success. Our platform provides you with the analytical tools to improve productivity, reduce waste, and achieve excellence. Your journey to efficiency begins here!",
    "Welcome aboard! With Snack Brands Australia's Performance Insights platform, access the latest metrics on production, packaging, and efficiency. Let's work together to transform data into powerful decisions and remarkable outcomes in your operations. Let's embark on this journey!"
]

st.set_page_config(
    page_title="Snack Brands Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styling immediately after page config
st.markdown(get_page_styling(), unsafe_allow_html=True)

# Initialize particles.js with proper height
if "show_animation" not in st.session_state:
    st.session_state.show_animation = True

if st.session_state.show_animation:
    components.html(get_particles_js(), height=800, scrolling=False)

# Initialize conversation history with welcome message
if "conversation_history" not in st.session_state:
    welcome_message = random.choice(WELCOME_MESSAGES)
    st.session_state.conversation_history = [{"role": "assistant", "content": welcome_message}]


def load_data(file_path, key):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
        return data[key]

def read_gif(file_path):
    with open(file_path, "rb") as file:
        contents = file.read()
    gif = base64.b64encode(contents).decode("utf-8")
    return gif

# Load environment variables
load_dotenv()
assistant_id = os.getenv("ASSISTANT_ID")
vector_store_id = os.getenv("VECTOR_STORE_ID")

# Sidebar content
def render_sidebar():
    # Logo at the top
    st.sidebar.image("assets/Snack-Brands.png", use_column_width=True)
    
    # Title and description
    st.sidebar.markdown("<h1 style='color: #2E86C1;'>Welcome to SBA Performance Hub</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-size: 14px;'>Your AI assistant for analyzing operational KPIs and plant performance metrics.</p>", unsafe_allow_html=True)
    
    # Key Features section
    st.sidebar.markdown("<h2 style='color: #2E86C1;'>Key Features</h2>", unsafe_allow_html=True)
    features = [
        "Analyze operational KPIs",
        "Track plant performance",
        "Calculate efficiency metrics",
        "Generate insights from production data",
        "Simulate performance scenarios"
    ]
    for feature in features:
        st.sidebar.markdown(f"<li style='margin-bottom: 5px;'>{feature}</li>", unsafe_allow_html=True)
    
    # How to Use section
    st.sidebar.markdown("<h2 style='color: #2E86C1;'>How to Use</h2>", unsafe_allow_html=True)
    usage_steps = [
        "Ask questions about KPIs and metrics",
        "Request specific calculations",
        "Compare performance periods",
        "Get insights and recommendations"
    ]
    st.sidebar.markdown("<ol style='padding-left: 20px;'>", unsafe_allow_html=True)
    for step in usage_steps:
        st.sidebar.markdown(f"<li style='margin-bottom: 5px;'>{step}</li>", unsafe_allow_html=True)
    st.sidebar.markdown("</ol>", unsafe_allow_html=True)
    
    # Add a separator for better organization
    st.sidebar.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)
    
    # Footer or additional links
    st.sidebar.markdown(
        "<p style='font-size: 12px; color: grey;'>Need help? Visit our <a href='https://snackbrands-ops.atlassian.net/servicedesk/customer/portal/1' target='_blank'>Help Center</a>.</p>",
        unsafe_allow_html=True
    )

def main():
    # Render sidebar
    render_sidebar()
    # Apply styling
    st.markdown(get_page_styling(), unsafe_allow_html=True)
    
    # Add particles.js background
    if st.session_state.show_animation:
        components.html(get_particles_js(), height=0)

    # Maintain thread and conversation context
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    # get thread id

    def get_thread_id():
        if st.session_state.thread_id is None:
            st.session_state.thread_id = AIAssistantManager.create_thread()
        return st.session_state.thread_id

    # Display conversation history with enhanced styling
    for message in st.session_state.conversation_history:
        with st.chat_message(
            message["role"],
            avatar=AVATAR_URLS.get(message["role"])
        ):
            st.write(message["content"])

    # User input
    if user_query := st.chat_input("Enter your query..."):
        with st.chat_message("user", avatar=AVATAR_URLS["user"]):
            st.write(user_query)
            
        # Add to conversation history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_query
        })

        # Assistant response with streaming
        with st.chat_message("assistant", avatar=AVATAR_URLS["assistant"]):
            output_area = st.empty()

            
            # Create thread and process response
            thread_id = get_thread_id()
            if not thread_id:
                st.error("Failed to create thread.")
                return
                
            client = AIAssistantManager.init_client()
            
            # Add message to thread
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_query
            )
            
            # Stream response
            event_handler = StreamlitEventHandler(output_area)
            try:
                with client.beta.threads.runs.stream(
                    thread_id=thread_id,
                    assistant_id=assistant_id,
                    instructions="",
                    event_handler=event_handler
                ) as stream:
                    current_response = ""
                    for delta in stream:
                        if hasattr(delta, 'data') and hasattr(delta.data, 'delta'):
                            if hasattr(delta.data.delta, 'content'):
                                for block in delta.data.delta.content:
                                    if hasattr(block, 'text') and hasattr(block.text, 'value'):
                                        text_chunk = block.text.value
                                        current_response += text_chunk
                                        output_area.markdown(current_response)
                    
                    # Add complete response to conversation history
                    if current_response:
                        st.session_state.conversation_history.append({
                            "role": "assistant",
                            "content": current_response
                        })
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()












