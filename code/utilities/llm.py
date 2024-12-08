import os
import logging
from typing import Optional
import openai
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables.config import RunnableConfig
from langchain_core.runnables import RunnableSequence
from sqlalchemy import create_engine


# Setup logging
logging.basicConfig(level=logging.INFO)

class ReportGenerator:

    DEFAULT_MODEL = "gpt-4o"

    def __init__(self, prompt: str, model: str, session_id: str = "default_session_id", temperature: float = 0.0):
        logging.info("Initializing ReportGenerator...")

        self.model_interface = os.getenv("OPENAI_MODEL_INTERFACE", "azure").lower()
        if self.model_interface not in ["openai", "azure"]:
            raise ValueError(f'Model interface "{self.model_interface}" not supported. Use "openai" or "azure".')

        if self.model_interface == "openai":
            openai.api_key = self.get_env_variable('OPENAI_API_KEY')
            self.model = ChatOpenAI(model=model, temperature=temperature)
        elif self.model_interface == "azure":
            openai.base_url = self.get_env_variable('AZURE_OPENAI_ENDPOINT')
            openai.api_key = self.get_env_variable('AZURE_OPENAI_API_KEY')
            openai.api_version = self.get_env_variable('OPENAI_API_VERSION')
            self.model = AzureChatOpenAI(deployment_name=model, temperature=temperature)
        
        self.prompt = self.set_prompt(prompt=prompt)
        self.chain = RunnableSequence(self.prompt | self.model)
        self.session_id = session_id
        self.set_message_history()

    @staticmethod
    def get_env_variable(var_name: str) -> str:
        """Get environment variable or raise an error if not set."""
        value = os.getenv(var_name)
        if not value:
            raise EnvironmentError(f"Environment variable {var_name} is not set")
        return value

    def get_config(self, session_id: Optional[str] = None) -> RunnableConfig:
        if session_id:
            self.session_id = session_id
        return RunnableConfig({"configurable": {"session_id": self.session_id}})

    @property
    def session_messages(self):
        return self.get_session_history(self.session_id).messages

    @staticmethod
    def clear_session(session_id: str):
        ReportGenerator.get_session_history(session_id).clear()

    @staticmethod
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        # Create a SQLAlchemy engine
        database_url = os.getenv('DATABASE_URL', 'sqlite:///memory.db')  # Default to SQLite in-memory DB
        engine = create_engine(database_url)

        # Pass the connection object to SQLChatMessageHistory
        return SQLChatMessageHistory(session_id, connection=engine)
    
    def set_message_history(self):
        self.with_message_history = \
            RunnableWithMessageHistory(
                self.chain,
                ReportGenerator.get_session_history,
                input_messages_key="messages"
            )

    def set_prompt(self, prompt):
        if not hasattr(self, "_cached_prompt"):
            self._cached_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", prompt),
                    MessagesPlaceholder(variable_name="messages"),
                ],
                template_format="mustache",
            )
        return self._cached_prompt

    def invoke_chain(self, question: str, session_id: Optional[str] = None, stream: bool = False):
        config = self.get_config(session_id)
        input_data = {"messages": [HumanMessage(content=question)]}

        if stream:
            return (r.content for r in self.with_message_history.stream(input_data, config=config))
        else:
            response = self.with_message_history.invoke(input_data, config=config)
            return response.content

    def ask_question(self, question: str, session_id: Optional[str] = None):
        return self.invoke_chain(question, session_id, stream=False)

    def ask_question_stream(self, question: str, session_id: Optional[str] = None):
        return self.invoke_chain(question, session_id, stream=True)
