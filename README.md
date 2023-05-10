# srt-translator
Translate .srt subtitle file with Microsoft Azure API

# How to use
1. Install dependency
```sh
pip install tox
```

2. Put your Azure resource information in `.env` ([How to create Azure Translator resource](https://learn.microsoft.com/en-us/azure/cognitive-services/translator/quickstart-translator#prerequisites))
```ini
TRANSLATION_KEY="<your-azure-translator-key>"
LOCATION="<your-azure-translator-location>"
```

3. Run command
```sh
# example: show help
$ tox run -e cli -- -h
cli: commands[0]> python -m srt_translator -h
usage: srt_translator [-h] {translate,split} ...

positional arguments:
  {translate,split}
    translate        Translate a .srt file. See available languages in https://learn.microsoft.com/en-us/azure/cognitive-services/translator/language-support#translation
    split            Split english and non-english subtitles of a .srt file and save them to '<input_file_name>.en.srt' and '<input_file_name>.other.srt' respectively   

options:
  -h, --help         show this help message and exit
  cli: OK (0.28=setup[0.05]+cmd[0.23] seconds)
  congratulations :) (0.38 seconds)
```
```sh
# example: show subcommand help
$ tox run -e cli -- translate -h
cli: commands[0]> python -m srt_translator translate -h
usage: srt_translator translate [-h] [--input_language INPUT_LANGUAGE] [--output_language OUTPUT_LANGUAGE] input_file output_file

Translate a .srt file. See available languages in https://learn.microsoft.com/en-us/azure/cognitive-services/translator/language-support#translation

positional arguments:
  input_file
  output_file

options:
  -h, --help            show this help message and exit
  --input_language INPUT_LANGUAGE, --in_lang INPUT_LANGUAGE
                        default=yue
  --output_language OUTPUT_LANGUAGE, --out_lang OUTPUT_LANGUAGE
                        default=zh-Hant
  cli: OK (0.30=setup[0.06]+cmd[0.23] seconds)
  congratulations :) (0.38 seconds)
```
