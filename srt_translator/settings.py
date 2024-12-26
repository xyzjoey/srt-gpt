from pathlib import Path

from pydantic import BaseSettings, DirectoryPath, HttpUrl, validator


class ProjectSettings(BaseSettings):
    root_dir: DirectoryPath
    dictionary_path: Path = None

    @validator("dictionary_path", always=True)
    def set_default_dictionary_path(cls, value, values):
        if not value:
            return values["root_dir"] / "dictionary.json"

        return value


class AzureSettings(BaseSettings):
    api_version: str = "3.0"
    translator_url: HttpUrl = "https://api.cognitive.microsofttranslator.com"
    translator_key: str
    location: str
