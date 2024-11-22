import streamlit as st
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from service.ai_service import AIAssistantManager
from service.run import StreamlitEventHandler

# Load environment variables from .env file
load_dotenv()

# Set up assistant ID
assistant_id = os.getenv("ASSISTANT_ID")

# set vector store ID
vector_store_id = os.getenv("VECTOR_STORE_ID")

# Initialize Streamlit session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


def main():
    st.title("Snack Brands Assistant")
    st.write("Chat with your AI Assistant in real-time!")

    # Display conversation history
    for entry in st.session_state.conversation_history:
        st.markdown(f"**You**: {entry['user']}")
        st.markdown(f"**Assistant**: {entry['assistant']}")

    # Refresh Button
    if st.button("Refresh Conversation"):
        st.experimental_rerun()

    # User input
    user_query = st.text_input("Enter your query:")
    if st.button("Submit"):
        if not user_query:
            st.warning("Please enter a query.")
            return

        if not assistant_id:
            st.error("Assistant ID not set.")
            return

        # Add the user's question to the conversation history
        st.session_state.conversation_history.append({"user": user_query, "assistant": ""})

        # Create a thread for the query
        thread_id = AIAssistantManager.create_thread()
        if not thread_id:
            st.error("Failed to create a thread.")
            return

        # Add the user query to the thread
        client = AIAssistantManager.init_client()
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_query,
        )

        # Placeholder for the assistant's response
        output_area = st.empty()

        # Use StreamlitEventHandler to stream responses dynamically
        event_handler = StreamlitEventHandler(output_area)

        try:
            with client.beta.threads.runs.stream(
                thread_id=thread_id,
                assistant_id=assistant_id,
                instructions="",  # Instructions already set in the assistant
                event_handler=event_handler,
            ) as stream:
                for delta in stream:
                    if hasattr(delta, 'data') and hasattr(delta.data, 'delta') and hasattr(delta.data.delta, 'content'):
                        for block in delta.data.delta.content:
                            if hasattr(block, 'text') and hasattr(block.text, 'value'):
                                text_chunk = block.text.value
                                st.session_state.conversation_history[-1]["assistant"] += text_chunk
                                output_area.markdown(st.session_state.conversation_history[-1]["assistant"])
                    elif hasattr(delta, 'tool_call'):
                        # Handle tool calls dynamically
                        if delta.tool_call.type == "file_search":
                            st.write("File search in progress...")
                        elif delta.tool_call.type == "code_interpreter":
                            st.write("Code execution in progress...")
        except Exception as e:
            st.error(f"An error occurred during streaming: {e}")

if __name__ == "__main__":
    main()












