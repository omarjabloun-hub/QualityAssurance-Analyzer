from crewai import LLM
from dotenv import load_dotenv
import os

load_dotenv()

model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

llm_gpt = LLM(
    model="openai/"+model_name, 
    temperature=0.2,
)