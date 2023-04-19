# srt-gpt
Request translation through OpenAI API and handle free trial users limitation.

Free trial users have very restricted [rate limit](https://platform.openai.com/docs/guides/rate-limits/what-are-the-rate-limits-for-our-api) (3 requests per minutes)

In order to translate smoothly, the script bundles as much text as possible in each request (target 2000 tokens).
In case rate limit exceeded, it waits until available again and continue.

# How to use
1. Install dependency
```sh
pip install tox
```

2. Put your OpenAI API key in `.env`
```ini
API_KEY="put_your_key_here"
```

3. Run command
```sh
# example: show help
$ python -m tox run -e cli -- -h

cli: commands[0]> python -m srt_gpt -h
usage: srt_gpt [-h] [--target_language TARGET_LANGUAGE] [--start START] [--end END] [--retry RETRY] input_file output_file

positional arguments:
  input_file
  output_file

options:
  -h, --help            show this help message and exit
  --target_language TARGET_LANGUAGE, --lang TARGET_LANGUAGE
                        default=english
  --start START         Index of first subtitle to translate. default=None
  --end END             Index of last subtitle to translate. default=None
  --retry RETRY         Retry until all request success default=True
  cli: OK (0.42=setup[0.05]+cmd[0.38] seconds)
  congratulations :) (0.52 seconds)
```
```sh
# example: start translation
$ python -m tox run -e cli -- --lang "中文書面語, 不要廣東話!" input.srt output.srt

cli: commands[0]> python -m srt_gpt --lang "中文書面語, 不要廣東話!" *** ***
22:36:10 INFO     [root  ] CAUTION: Please make sure your IP is in supported country by OpenAI or your account can be blocked
22:36:10 INFO     [root  ] Loading subtitles from '***'...
22:36:10 INFO     [root  ] Successfully loaded 775 subtitles!
22:36:10 INFO     [root  ] Target language: 中文書面語, 不要廣東話!
22:36:10 INFO     [root  ] Total translation range: 1~776
22:36:10 INFO     [root  ] Start translation
22:36:10 INFO     [root  ] Make request 1 (subtitle range: 1~102, estimated tokens: 1997)...
22:38:16 INFO     [openai] message='OpenAI API response' path=https://api.openai.com/v1/chat/completions processing_ms=124988 request_id=*** response_code=200
22:38:16 INFO     [root  ] Translation result {***}
22:38:16 INFO     [root  ] Saving subtitles to '***'...
22:38:16 INFO     [root  ] Successfully Saved subtitles!
22:38:16 INFO     [root  ] Make request 2 (subtitle range: 103~208, estimated tokens: 1990)...
```
