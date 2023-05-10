import logging

from pydantic import FilePath
import srt

from ..utils.types import CommandInputs


class Inputs(CommandInputs):
    input_file: FilePath
    tolerance: float = 0.9


class Command:
    description = "Split english and non-english subtitles of a .srt file and save them to '<input_file_name>.en.srt' and '<input_file_name>.other.srt' respectively"

    def start(self):
        inputs = Inputs.parse_from_args()

        subtitles = None
        subtitles_en = []
        subtitles_other = []

        with inputs.input_file.open(encoding="utf-8") as f:
            subtitles = list(srt.parse(f.read()))

        for subtitle in subtitles:
            en_count = sum(c.isascii() for c in subtitle.content)
            en_percent = en_count / len(subtitle.content)
            # logging.info(f"({en_percent}) {subtitle.content}")

            if en_percent > inputs.tolerance:
                subtitles_en.append(subtitle)
            else:
                subtitles_other.append(subtitle)

        output_file_en = inputs.input_file.with_suffix(".en.srt")
        output_file_other = inputs.input_file.with_suffix(".other.srt")

        output_file_en.write_text(srt.compose(subtitles_en), encoding="utf-8")
        output_file_other.write_text(srt.compose(subtitles_other), encoding="utf-8")

        logging.info(f"Successfully save english part to {output_file_en}")
        logging.info(f"Successfully save non english part to {output_file_other}")
