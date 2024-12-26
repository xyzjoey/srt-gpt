from pathlib import Path
import json
import logging
import uuid

from pydantic import Field, FilePath
import srt
import requests

from ..settings import ProjectSettings, AzureSettings
from ..utils.types import CommandInputs


class Inputs(CommandInputs):
    input_file: FilePath
    output_file: Path
    input_language: str = Field("yue", alias="ilang")
    output_language: str = Field("zh-Hant", alias="olang")


class Command:
    description = (
        "Translate a .srt file. See available languages in https://learn.microsoft.com/en-us/azure/cognitive-services/translator/language-support#translation"
    )

    def start(self, inputs: Inputs, project_settings: ProjectSettings, azure_settings: AzureSettings):
        dictionary = self._build_dictionary(project_settings.dictionary_path, inputs.output_language)

        url = f"{azure_settings.translator_url}/translate"

        headers = {
            "Ocp-Apim-Subscription-Key": azure_settings.translator_key,
            "Ocp-Apim-Subscription-Region": azure_settings.location,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }

        params = {
            "api-version": azure_settings.api_version,
            "from": inputs.input_language,
            "to": [inputs.output_language],
        }

        subtitles = []

        with inputs.input_file.open(encoding="utf-8") as f:
            subtitles = list(srt.parse(f.read()))

        logging.info(f"Loaded {len(subtitles)} subtitles from '{inputs.input_file}'")
        logging.info(f"Start translation...")

        i = 0
        interval = 100

        while i < len(subtitles):
            j = min(i + interval, len(subtitles))

            body = [{"text": self._inject_dictionary(subtitle.content, dictionary)} for subtitle in subtitles[i:j]]
            response = requests.post(url, params=params, headers=headers, json=body)
            response_json = response.json()

            if not response.ok:
                logging.warn(f"Failed to translate subtitles (start_index={subtitles[i].index}, end_index={subtitles[j].index}). Response: {response_json}")
            else:
                logging.debug(response_json)

                for k, result in enumerate(response_json):
                    translated_text = result["translations"][0]["text"]
                    subtitles[i + k].content = translated_text

                inputs.output_file.write_text(srt.compose(subtitles), encoding="utf-8")
                logging.info(f"Translation progress: {j + 1}/{len(subtitles)}")

            i += interval

        logging.info(f"Successfully saved translated subtitles to '{inputs.output_file}'!")

    def _build_dictionary(self, dictionary_path, target_language):
        dictionary = {}

        if dictionary_path.is_file():
            with open(dictionary_path, encoding="utf-8") as f:
                full_dictionary = json.load(f)

                for phrase, v in full_dictionary.items():
                    translated_phrase = v.get(target_language)

                    if translated_phrase:
                        dictionary[phrase] = f'<mstrans:dictionary translation="{translated_phrase}">{phrase}</mstrans:dictionary>'

        return dictionary

    def _inject_dictionary(self, text, dictionary):
        new_text = text

        for phrase, phrase_with_dictionary in dictionary.items():
            new_text = new_text.replace(phrase, phrase_with_dictionary)

        return new_text
