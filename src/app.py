import streamlit as st
import streamlit.components.v1 as components
import logging
import yaml
import random
import os
import base64
from datetime import datetime
import time
import re 
import tempfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image
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

def show_welcome_animation():
    """Display welcome animation on first load"""
    with st.spinner("Loading SBA Performance Hub..."):
        time.sleep(1)
    ##st.balloons()

def display_welcome_banner():
    """Display time-based welcome banner"""
    current_hour = datetime.now().hour
    greeting = "Good Morning" if current_hour < 12 else "Good Afternoon" if current_hour < 17 else "Good Evening"
        
    st.markdown(f"""
        <div style='padding: 1.5rem; border-radius: 10px; background-color: rgba(46, 134, 193, 0.1); 
                    border: 1px solid rgba(46, 134, 193, 0.2); margin-bottom: 1rem;'>
            <h2 style='color: #2E86C1; margin: 0;'>{greeting}! 👋</h2>
            <p style='margin: 0.5rem 0 0 0;'>Welcome to SBA Performance Hub. How can I assist you today?</p>
        </div>
    """, unsafe_allow_html=True)

st.set_page_config(
    page_title="Snack Brands Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styling immediately after page config
st.markdown(get_page_styling(), unsafe_allow_html=True)

# Initialize session states
if "show_animation" not in st.session_state:
    st.session_state.show_animation = True
if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False
if "conversation_history" not in st.session_state:
    welcome_message = random.choice(WELCOME_MESSAGES)
    st.session_state.conversation_history = [{"role": "assistant", "content": welcome_message}]
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if st.session_state.show_animation:
    components.html(get_particles_js(), height=800, scrolling=False)

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

def send_email(to_email, content):
    """Send email with the specified content"""
    # Email configuration
    from_email = "abdia980@gmail.com"
    subject = "SBA Performance Hub - Your Requested Information"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Add body
    msg.attach(MIMEText(content, 'plain'))
    
    try:
        # Create SMTP session
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            password = os.getenv("EMAIL_PASSWORD")
            if not password:
                raise ValueError("EMAIL_PASSWORD environment variable is not set")
            server.login(from_email, password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def wait_for_run_completion(client, thread_id, run_id, timeout=60):
    """Wait for the assistant's run to complete"""
    start_time = time.time()
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status == "completed":
            return True
        elif run.status == "failed":
            st.error("Assistant run failed")
            return False
        elif time.time() - start_time > timeout:
            st.error("Request timed out")
            return False
        time.sleep(1)

def process_email_query(email, query):
    """Process email query and send response"""
    try:
        thread_id = get_thread_id()
        if not thread_id:
            st.sidebar.error("Failed to create thread.")
            return False

        client = AIAssistantManager.init_client()
        if not client:
            st.sidebar.error("Failed to initialize AI client.")
            return False

        # Create message in thread
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=query,
            timeout=30
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        # Wait for completion
        if not wait_for_run_completion(client, thread_id, run.id):
            return False

        # Get messages after completion
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        latest_response = None

        # Get the latest assistant response
        for msg in messages.data:
            if msg.role == "assistant":
                latest_response = msg.content[0].text.value
                break

        if not latest_response:
            st.sidebar.error("No response generated")
            return False

        # Send email
        if send_email(email, latest_response):
            return True
        return False

    except Exception as e:
        st.sidebar.error(f"Error processing query: {str(e)}")
        return False


def process_query(query, output_area):
    """Process a user query and generate response"""
    thread_id = get_thread_id()
    if not thread_id:
        st.error("Failed to create thread.")
        return

    client = AIAssistantManager.init_client()

    # Log request for verbose mode
    if st.session_state.verbose_logging:
        st.sidebar.markdown(f"📝 **User Query:** {query}")
        start_time = time.time()
    
    # Add message to thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=query,
        timeout=30
    )
    
    # Stream response
    event_handler = StreamlitEventHandler(output_area)
    try:
        with client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions="",
            event_handler=event_handler,
            timeout=30
        ) as stream:
            current_response = ""
            for delta in stream:
                if hasattr(delta, 'data') and hasattr(delta.data, 'delta'):
                    # Process content blocks
                    content_blocks = getattr(delta.data.delta, 'content', [])
                    if not content_blocks:
                        continue  # Skip if no content blocks
                    
                    for block in content_blocks:
                        # Handle text content
                        if hasattr(block, 'text') and hasattr(block.text, 'value'):
                            text_chunk = block.text.value
                            current_response += text_chunk
                            output_area.markdown(current_response)
                        
                        # Handle image content
                        elif hasattr(block, 'image_file') and block.image_file:
                            try:
                                image_file = block.image_file.file_id
                                if not image_file:
                                    st.error("Image file ID is missing.")
                                    continue
                                
                                # Fetch and process image
                                image_data = client.files.content(image_file).read()
                                temp_file = tempfile.NamedTemporaryFile(delete=False)
                                temp_file.write(image_data)
                                temp_file.close()
                                
                                # Open and display image
                                image = Image.open(temp_file.name)
                                st.image(image, use_column_width=True)
                            except Exception as e:
                                st.error(f"Error processing image: {e}")
                            finally:
                                # Clean up temporary file
                                if temp_file:
                                    os.unlink(temp_file.name)
                        
                        # Handle unknown content types
                        else:
                            st.warning(f"Unexpected content type: {block.type}")

            # Log response time for verbose mode
            if st.session_state.verbose_logging:
                end_time = time.time()
                response_time = round(end_time - start_time, 2)
                st.sidebar.markdown(f"⏱️ **Response Time:** {response_time} seconds")
                st.sidebar.markdown(f"**Response:** {content_blocks}")
            
            # Add complete response to conversation history
            if current_response.strip():
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": current_response.strip()
                })
    except Exception as e:
        st.error(f"An error occurred: {e}")
        if st.session_state.verbose_logging:
            st.sidebar.error(f"An error occurred: {e}")

     


def get_thread_id():
    """Get or create thread ID"""
    if st.session_state.thread_id is None:
        st.session_state.thread_id = AIAssistantManager.create_thread()
    return st.session_state.thread_id

def render_sidebar():
    """Render sidebar with enhanced features"""
    st.sidebar.image("assets/Snack-Brands.png", use_column_width=True)
    
    # Email notification section
    enable_email = st.sidebar.checkbox("📧 Enable Email Notifications", 
                                     key="enable_email",
                                     help="Get answers sent to your email")
    
    if enable_email:
        email = st.sidebar.text_input("Enter your email address",
                                    key="email_address",
                                    placeholder="your.email@example.com")
        
        email_query = st.sidebar.text_area("What information would you like to receive?",
                                         key="email_query",
                                         placeholder="E.g., Daily KPI summary, Weekly efficiency report...")
        
        if st.sidebar.button("Send to Email"):
            if not email or not email_query:
                st.sidebar.error("Please provide both email and query.")
            else:
                with st.spinner("Processing your request..."):
                    if process_email_query(email, email_query):
                        st.sidebar.success("✅ Email sent successfully!")
                    else:
                        st.sidebar.error("❌ Failed to process request")
    
    

    #instatiate verbose logging
    verbose_logging = st.sidebar.checkbox("📝 Verbose Logging", key="verbose_logging", help="Enable verbose logging for debugging")

    # Dev Mode toggle
    if st.sidebar.checkbox("🛠️ Dev Mode", key="dev_mode", help="Enable developer mode for debugging"):
                if st.session_state.thread_id:
                    st.sidebar.markdown(
                f"""<div style='padding: 10px; background-color: rgba(255,255,255,0.1); 
                    border-radius: 5px; margin: 10px 0;'>
                    <small>Session ID: {st.session_state.thread_id[:8]}...</small>
                </div>""",
                unsafe_allow_html=True
            )

                if verbose_logging:
                    st.sidebar.markdown("<small>Verbose logging enabled.</small>", unsafe_allow_html=True)

                
    # Add refresh button at the top
    if st.sidebar.button("🔄 New Conversation", key="refresh_button",
                        help="Start a new conversation"):
        st.session_state.conversation_history = []
        st.session_state.thread_id = None
        st.session_state.welcome_shown = False
        st.rerun()
    
    
    # Quick Actions section
    st.sidebar.markdown("<h2 style='color: #2E86C1;'>Quick Actions</h2>", unsafe_allow_html=True)
    quick_actions = {
        "📊 View Overall KPIs": "Show me the overall KPIs for the current month",
        "🏭 Plant Performance": "Analyze plant performance metrics",
        "⏱️ Efficiency Analysis": "Calculate current efficiency metrics",
        "📈 Production Trends": "Show production trends over the last 3 months",
        "🎯 Target vs Actual": "Compare target vs actual performance"
    } # TODO: Use as presets for user queries
    
    selected_action = st.sidebar.selectbox(
        "Choose a quick action",
        list(quick_actions.keys()),
        key="quick_actions"
    )
    
    if st.sidebar.button("Execute Action"):
        return quick_actions[selected_action]
    
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
    
    st.sidebar.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)
    
    st.sidebar.markdown(
        """<p style='font-size: 12px; color: grey;'>Need help? Visit our 
        <a href='https://snackbrands-ops.atlassian.net/servicedesk/customer/portal/1' target='_blank'>Help Center</a>.</p>""",
        unsafe_allow_html=True
    )
    
    return None

def main():
    # Show welcome animation only once per session
    if not st.session_state.welcome_shown:
        show_welcome_animation()
        st.session_state.welcome_shown = True
    
    # Render sidebar and get any quick action query
    quick_action_query = render_sidebar()
    
    # Apply styling
    st.markdown(get_page_styling(), unsafe_allow_html=True)
    
    # Add particles.js background
    if st.session_state.show_animation:
        components.html(get_particles_js(), height=0)

    # Display welcome banner
    display_welcome_banner()
    
    # Display conversation history with enhanced styling
    for message in st.session_state.conversation_history:
        with st.chat_message(
            message["role"],
            avatar=AVATAR_URLS.get(message["role"])
        ):
            st.write(message["content"])

    # Process quick action if selected
    if quick_action_query:
        with st.chat_message("user", avatar=AVATAR_URLS["user"]):
            st.write(quick_action_query)
        
        st.session_state.conversation_history.append({
            "role": "user",
            "content": quick_action_query
        })
        
        with st.chat_message("assistant", avatar=AVATAR_URLS["assistant"]):
            output_area = st.empty()
            process_query(quick_action_query, output_area)

    # User input
    if user_query := st.chat_input("Enter your query..."):
        with st.chat_message("user", avatar=AVATAR_URLS["user"]):
            st.write(user_query)
            
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_query
        })

        with st.chat_message("assistant", avatar=AVATAR_URLS["assistant"]):
            output_area = st.empty()
            process_query(user_query, output_area)

if __name__ == "__main__":
    main()












