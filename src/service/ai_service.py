import os
import logging
import openai
from typing import Dict, List
from contextlib import ExitStack


class AIAssistantManager:
    @staticmethod
    def init_client():
        """Initialize OpenAI client."""
        try:
            # Set the OpenAI API key globally
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            # Validate the API key
            if not openai.api_key:
                raise ValueError("OpenAI API key is not set. Please configure the 'OPENAI_API_KEY' environment variable.")
            
            # Return the OpenAI module for further use
            return openai
        except Exception as e:
            logging.error(f"Error initializing OpenAI client: {e}")
            return None

    @staticmethod
    def create_ai_assistant(name=None, model=None, instructions=None, tools=None):
        """Create a new AI assistant."""
        client = AIAssistantManager.init_client()
        try:
            # Assign default values if parameters are not provided
            name = name or "SBA-Data-Assistant"
            model = model or "gpt-4o"
            instructions = instructions or "I am an AI assistant for data analysis and reporting."
            tools = tools or [{"type": "file_search"}]

            # Create the assistant
            assistant = client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model=model,
                tools=tools,
                timeout=30
            )
            logging.info(f"Successfully created AI assistant: {name}")
            return assistant.id
        except Exception as e:
            logging.error(f"Error creating AI assistant: {e}")
            return None

    @staticmethod
    def create_vector_store(vector_name=None, directory=None):
        """Create a vector store for uploading files."""
        client = AIAssistantManager.init_client()
        try:
            vector_name = vector_name or "SBA-Manufacturing-Data"
            directory = directory or "data"

            if not os.path.isdir(directory):
                raise ValueError(f"Directory not found: {directory}")

            # Create the vector store
            vector_store = client.beta.vector_stores.create(name=vector_name)

            # Upload files from the specified directory
            file_streams = []
            supported_formats = [".csv", ".txt", ".json", ".xlsx", ".py", ".docx", ".pdf"]
            with ExitStack() as stack:
                for file in os.listdir(directory):
                    file_path = os.path.join(directory, file)

                    # Check if the file format is supported
                    if not any(file_path.endswith(fmt) for fmt in supported_formats):
                        logging.warning(f"Unsupported file format: {file_path}")
                        continue
                    try:
                        file_stream = stack.enter_context(open(file_path, "rb"))
                        file_streams.append(file_stream)
                    except Exception as e:
                        logging.error(f"Error reading file: {file_path} - {e}")

                if not file_streams:
                    raise ValueError(f"No supported files found in directory: {directory}")

            # Upload files to the vector store
            file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id,
                files=file_streams
            )
            logging.info(f"Successfully created vector store: {vector_name}")
            return vector_store.id
        except Exception as e:
            logging.error(f"Error creating vector store: {e}")
            return None

    @staticmethod
    def update_assistant(assistant_id, vector_store_id, tool="file_search"):
        """Update an existing AI assistant with a vector store."""
        client = AIAssistantManager.init_client()
        try:
            if not assistant_id:
                raise ValueError("Assistant ID must be provided.")
            if not vector_store_id:
                raise ValueError("Vector Store ID must be provided.")

            assistant = client.beta.assistants.retrieve(assistant_id)

            assistant = client.beta.assistants.update(
                assistant_id,
                tool_resources={tool: {"vector_store_ids": [vector_store_id]}},
            )
            logging.info(f"Successfully updated AI assistant {assistant_id} with vector store {vector_store_id}.")
            return assistant.id
        except Exception as e:
            logging.error(f"Error updating AI assistant: {e}")
            return None

    @staticmethod
    def get_existing_assistant_metadata(assistant_id):
        """Retrieve metadata for an existing assistant."""
        client = AIAssistantManager.init_client()
        try:
            assistant = client.beta.assistants.retrieve(assistant_id)
            return assistant
        except Exception as e:
            logging.error(f"Error retrieving assistant: {e}")
            return None

    @staticmethod
    def create_thread():
        """Create a new thread for conversations."""
        client = AIAssistantManager.init_client()
        try:
            thread =  client.beta.threads.create(timeout=30)
            return thread.id
        except Exception as e:
            logging.error(f"Error creating thread: {e}")
            return None

    @staticmethod
    def create_conversation(thread_id, query):
        """Initialize a conversation within a thread."""
        client = AIAssistantManager.init_client()
        try:
            message = client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=query
            )
            return message
        except Exception as e:
            logging.error(f"Error creating conversation: {e}")
            return None


