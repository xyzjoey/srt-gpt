from argparse import ArgumentParser
import asyncio
import logging
from pathlib import Path
from typing import Optional

import openai
from pydantic import BaseModel, Field, FilePath
import srt
import tiktoken

from .settings import APISettings


class Inputs(BaseModel):
    input_file: FilePath
    output_file: Path
    target_language: str = Field("english", alias="lang")
    start: Optional[int] = Field(description="Index of first subtitle to translate.")
    end: Optional[int] = Field(description="Index of last subtitle to translate.")
    retry: bool = Field(True, description="Retry until all request success")

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def parse_from_args(cls):
        parser = ArgumentParser("srt_gpt")

        for field_name, field in Inputs.__fields__.items():
            help = field.field_info.description or ""
            if field.required:
                parser.add_argument(field_name, help=help)
            else:
                arg_names = [f"--{field_name}"]
                if field.has_alias:
                    arg_names.append(f"--{field.alias}")
                parser.add_argument(*arg_names, help=f"{help}\ndefault={field.default}", default=field.default)

        args = parser.parse_args()
        return cls(**args.__dict__)


class Tokenizer:
    tokens_per_msg = 4
    end_tokens = 3

    @classmethod
    def count_messages_token(cls, messages, encoding):
        encoder = tiktoken.encoding_for_model(encoding)

        count = 0
        count += len(messages) * cls.tokens_per_msg
        count += sum([sum([len(encoder.encode(value)) for value in msg.values()]) for msg in messages])
        count += cls.end_tokens

        return count


class Subtitle:
    @staticmethod
    def load(file_path: FilePath) -> list[srt.Subtitle]:
        file_path = file_path.resolve()
        logging.info(f"Loading subtitles from '{file_path}'...")

        try:
            with file_path.open(encoding="utf-8") as f:
                subtitles = list(srt.parse(f.read()))
                logging.info(f"Successfully loaded {len(subtitles)} subtitles!")
                return subtitles

        except Exception as e:
            raise ValueError(f"Failed to parse subtitle file: {e}")

    @staticmethod
    def save(subtitles: list[srt.Subtitle], file_path: Path):
        file_path = file_path.resolve()
        logging.info(f"Saving subtitles to '{file_path}'...")

        file_content = srt.compose(subtitles)
        file_path.write_text(file_content, encoding="utf-8")
        logging.info(f"Successfully Saved subtitles!")


class Utils:
    @staticmethod
    def find_index(iterable, condition):
        for i, item in enumerate(iterable):
            if condition(item):
                return i

        return None


class MessageTemplate:
    def __init__(self, target_language: str):
        self.instructions = (
            "You are a program responsible for translating subtitles. "
            "Your task is to output the specified target language based on the input text. "
            # "Please do not create the following subtitles on your own. "
            "Please do not output any text other than the translation. "
            "You will receive the subtitles as python dict format. Each dict value is a subtitle. Please translate then output in the same format. "
            "You must not change the key, merge or split any value of the dict. "
            # "Please transliterate the person's name into the local language. "
            f"Target language: {target_language}"
        )

    def get(self, subtitles: list[srt.Subtitle]):
        messages = [
            {
                "role": "system",
                "content": self.instructions,
            },
            {
                "role": "user",
                "content": str({subtitle.index: subtitle.content for subtitle in subtitles}),
            },
        ]
        return messages


class TranslationApp:
    def __init__(self, settings: APISettings):
        self.settings = settings
        self.request_count = 0

    def estimate_max_request_index(self, target_language: str, subtitles: list[srt.Subtitle], start_i: int, end_i: int):
        max_tokens = 2000  # actual max is 4096, reserve half for response

        message_template = MessageTemplate(target_language)
        max_i = min(start_i + 99, end_i)

        while Tokenizer.count_messages_token(message_template.get(subtitles[start_i : max_i + 1]), self.settings.model) < max_tokens:
            if max_i == end_i:
                break
            max_i += 1

        while Tokenizer.count_messages_token(message_template.get(subtitles[start_i : max_i + 1]), self.settings.model) > max_tokens:
            if max_i == start_i:
                break
            max_i -= 1

        tokens = Tokenizer.count_messages_token(message_template.get(subtitles[start_i : max_i + 1]), self.settings.model)

        return max_i, tokens

    async def request_translation(self, target_language: str, subtitles: list[srt.Subtitle]) -> tuple[dict, bool]:
        self.request_count += 1

        message_template = MessageTemplate(target_language)
        messages = message_template.get(subtitles)
        completion = None
        translated_subtitles = None

        while completion is None:
            try:
                completion = await openai.ChatCompletion.acreate(
                    model=self.settings.model,
                    messages=messages,
                )
            except openai.error.RateLimitError as e:
                logging.warn(e.user_message)
                logging.info("Retry in 20s...")
                await asyncio.sleep(20)  # TODO: compute wait time

        try:
            translated_subtitles = dict(eval(completion.choices[0].message.content))
        except Exception as e:
            logging.error(f"Unexpected translation format: {e}")
            return None, False

        if len(translated_subtitles) != len(subtitles):
            logging.warn(f"Unexpected number of translated subtitles (expected {len(subtitles)}, get {len(translated_subtitles)}")
            return translated_subtitles, False

        logging.info(f"Translation result {translated_subtitles}")

        return translated_subtitles, True

    async def start(self, inputs: Inputs):
        subtitles = Subtitle.load(inputs.input_file)

        if len(subtitles) == 0:
            logging.warn("No subtitles to translate")
            logging.info("Done")
            return

        if inputs.start is None:
            inputs.start = subtitles[0].index

        if inputs.end is None:
            inputs.end = subtitles[-1].index

        logging.info(f"Target language: {inputs.target_language}")
        logging.info(f"Total translation range: {inputs.start}~{inputs.end}")
        logging.info("Start translation")

        def _apply_translation(start_i: int, translated_subtitles: dict):
            for i, translated_text in enumerate(translated_subtitles.values()):
                subtitles[start_i + i].content = translated_text

            Subtitle.save(subtitles, inputs.output_file)

        failed_ranges = []
        start_i = Utils.find_index(subtitles, lambda subtitle: subtitle.index == inputs.start)
        end_i = Utils.find_index(subtitles, lambda subtitle: subtitle.index == inputs.end)

        while start_i <= end_i:
            max_i, tokens = self.estimate_max_request_index(inputs.target_language, subtitles, start_i, end_i)

            logging.info(
                f"Make request {self.request_count + 1} (subtitle range: {subtitles[start_i].index}~{subtitles[max_i].index}, estimated tokens: {tokens})..."
            )

            translated_subtitles, success = await self.request_translation(inputs.target_language, subtitles[start_i : max_i + 1])

            if not success:
                failed_ranges.append((start_i, max_i))

            if translated_subtitles is not None:
                _apply_translation(start_i, translated_subtitles)

            start_i = max_i + 1

        if not inputs.retry and len(failed_ranges) > 0:
            logging.warn(f"Translation done with failed range: {failed_ranges}")

        if inputs.retry and len(failed_ranges) > 0:
            logging.info(f"Start retry on failed ranges: {failed_ranges}...")

            for start_i, max_i in failed_ranges:
                success = False

                while not success:
                    logging.info(f"Make request {self.request_count + 1} (subtitle range: {subtitles[start_i].index}~{subtitles[max_i].index})...")

                    translated_subtitles, success = await self.request_translation(inputs.target_language, subtitles[start_i : max_i + 1])

                    if success:
                        _apply_translation(start_i, translated_subtitles)

        logging.info(f"Translation done!")
