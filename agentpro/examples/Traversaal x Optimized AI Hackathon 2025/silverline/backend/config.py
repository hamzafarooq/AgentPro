import tomllib
from os import getenv
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()

with open("pyproject.toml", "rb") as f:
    poetry: dict[str] = tomllib.load(f).get("tool", {}).get("poetry", {})
    name = poetry.get("name")
    description = poetry.get("description")
    version = poetry.get("version")

class ConfigClass(BaseModel):
    app_name: str
    description: str
    version: str
    root_path: str
    api_key: Optional[str]
    openai_api_key: Optional[str]
    openai_realtime_model: Optional[str]
    backend_url: Optional[str]
    classifier_model: Optional[str]

CONFIG = ConfigClass(
    app_name = name,
    description = description,
    version = version,
    root_path="/ai",
    api_key = getenv("API_KEY") if getenv("API_KEY") else None,
    openai_api_key=getenv("OPENAI_API_KEY") if getenv("OPENAI_API_KEY") else None,
    openai_realtime_model = getenv("OPENAI_REALTIME_MODEL") if getenv("OPENAI_REALTIME_MODEL") else None,
    backend_url = getenv("BACKEND_URL") if getenv("BACKEND_URL") else None,
    classifier_model = getenv("CLASSIFIER_MODEL") if getenv("CLASSIFIER_MODEL") else None
)
