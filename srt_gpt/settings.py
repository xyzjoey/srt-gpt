import logging

import openai
from pydantic import BaseSettings, DirectoryPath


class ProjectSettings(BaseSettings):
    root_dir: DirectoryPath


class APISettings(BaseSettings):
    api_key: str
    model: str = "gpt-3.5-turbo"

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        openai.api_key = self.api_key

        logging.info("CAUTION: Please make sure your IP is in supported country by OpenAI or your account can be blocked")
