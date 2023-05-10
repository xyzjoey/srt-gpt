from pydantic import BaseSettings, DirectoryPath, HttpUrl


class ProjectSettings(BaseSettings):
    root_dir: DirectoryPath


class AzureSettings(BaseSettings):
    api_version: str = "3.0"
    translator_url: HttpUrl = "https://api.cognitive.microsofttranslator.com"
    translator_key: str
    location: str
