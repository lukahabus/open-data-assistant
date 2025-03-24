"""
DCAT Assistant - A LangChain-based assistant for interacting with DCAT metadata.

This module provides a LangChain-based assistant that helps users interact with
DCAT metadata, including searching for datasets, answering questions about
datasets, and suggesting related datasets.
"""

import os
import sys
from typing import List, Dict, Any, Optional, Tuple, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage

# Dodaj parent direktorij u sys.path za ispravno učitavanje modula
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Nakon dodavanja parent direktorija možemo uvesti module iz dcat paketa
from dcat.dcat_embedding import DCATEmbedder
from dcat.dcat_metadata import (
    Catalog,
    Dataset,
    Distribution,
    DataService,
    load_catalog_from_json,
)

# Load environment variables
load_dotenv()


class DCATAssistant:
    """A LangChain-based assistant for interacting with DCAT metadata."""

    def __init__(self, dcat_embedder: DCATEmbedder, model_name: str = "gpt-3.5-turbo"):
        """Initialize the DCATAssistant.

        Args:
            dcat_embedder: The DCATEmbedder to use for embedding DCAT metadata.
            model_name: The name of the model to use for the assistant. Defaults to "gpt-3.5-turbo".
        """
        self.dcat_embedder = dcat_embedder
        self.llm = ChatOpenAI(model_name=model_name, temperature=0)

        # Create the system message
        system_template = """
        You are a helpful assistant for interacting with DCAT (Data Catalog Vocabulary) metadata.
        You can help users find datasets, answer questions about datasets, and suggest related datasets.
        
        When a user asks about a dataset, try to provide as much relevant information as possible,
        including the title, description, publisher, and any other relevant metadata.
        
        When a user asks a question that requires analyzing a dataset, try to answer the question
        using the dataset metadata. If you don't have enough information to answer the question,
        ask the user for more information or suggest a dataset that might help.
        
        Always be friendly, concise, and helpful.
        
        Context: {context}
        """

        system_message_prompt = SystemMessagePromptTemplate.from_template(
            system_template
        )
        human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")

        self.chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        # Create the retrieval chain
        self.chain = None

    def initialize_chain(self):
        """Initialize the ConversationalRetrievalChain."""
        if not self.dcat_embedder.vector_store:
            raise ValueError(
                "DCATEmbedder does not have a vector store. Please call embed_catalog first."
            )

        retriever = self.dcat_embedder.vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 5}
        )

        # Modern approach using LCEL
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.chat_prompt.messages[0].prompt.template),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        from langchain.chains import (
            create_history_aware_retriever,
            create_retrieval_chain,
        )
        from langchain.chains.combine_documents import create_stuff_documents_chain

        # Create a prompt for contextualizing questions with chat history
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history.",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        # Create a history-aware retriever
        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, contextualize_q_prompt
        )

        # Create a question-answering chain
        qa_chain = create_stuff_documents_chain(self.llm, qa_prompt)

        # Create the retrieval chain
        self.chain = create_retrieval_chain(history_aware_retriever, qa_chain)

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query.

        Args:
            query: The user query to process.

        Returns:
            A dictionary containing the answer and source documents.
        """
        if not self.chain:
            self.initialize_chain()

        # Process the query with the chain
        result = self.chain.invoke(
            {"input": query, "chat_history": []}  # Empty chat history for now
        )

        # Format the result to match the expected return structure
        return {
            "answer": result["answer"],
            "source_documents": result.get("context", []),
        }

    def search_datasets(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Search for datasets matching a query.

        Args:
            query: The query to search for.
            k: The number of results to return. Defaults to 5.

        Returns:
            A list of tuples containing the document and its similarity score.
        """
        return self.dcat_embedder.semantic_search(query, k=k)

    def get_dataset_info(self, dataset_id: str) -> Optional[str]:
        """Get information about a dataset.

        Args:
            dataset_id: The ID of the dataset to get information about.

        Returns:
            A string containing information about the dataset, or None if not found.
        """
        dataset_doc = self.dcat_embedder.get_dataset_by_id(dataset_id)
        if not dataset_doc:
            return None

        return dataset_doc.page_content

    def suggest_related_datasets(self, dataset_id: str, k: int = 3) -> List[str]:
        """Suggest datasets related to a specific dataset.

        Args:
            dataset_id: The ID of the dataset to find related datasets for.
            k: The number of results to return. Defaults to 3.

        Returns:
            A list of strings containing information about related datasets.
        """
        related_docs = self.dcat_embedder.find_related_datasets(dataset_id, k=k)
        return [doc.page_content for doc in related_docs]

    def answer_question_about_dataset(self, dataset_id: str, question: str) -> str:
        """Answer a question about a specific dataset.

        Args:
            dataset_id: The ID of the dataset to answer a question about.
            question: The question to answer.

        Returns:
            A string containing the answer to the question.
        """
        dataset_doc = self.dcat_embedder.get_dataset_by_id(dataset_id)
        if not dataset_doc:
            return f"Dataset with ID {dataset_id} not found."

        # Create a prompt specifically about this dataset
        prompt = f"""
        Based on the following dataset information, please answer the question:
        
        {dataset_doc.page_content}
        
        Question: {question}
        """

        # Use the LLM to generate an answer
        result = self.llm.invoke(prompt)
        return result.content
