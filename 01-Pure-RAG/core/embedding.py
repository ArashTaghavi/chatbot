
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parent / ".env")

client = OpenAI()

def embed(texts: list[str], model: str = "text-embedding-3-large"):

    response = client.embeddings.create(model=model, input=texts)

    return np.array([item.embedding for item in response.data])
