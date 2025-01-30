import os
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI LLM
llm = OpenAI(api_key=openai_api_key)

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["street_name", "street_info"],
    template="""
    You are a chatbot that provides information about street names in Zagreb.
    Street Name: {street_name}
    Street Info: {street_info}
    If the street is named after a famous person, provide additional information about the person.
    """,
)

# Create the LLM chain
chain = LLMChain(llm=llm, prompt=prompt_template)


# Function to get additional info about a famous person
def get_famous_person_info(person_name):
    response = chain.run({"street_name": person_name, "street_info": ""})
    return response
