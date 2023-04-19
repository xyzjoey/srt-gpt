import asyncio

from .app import Inputs, TranslationApp
from .settings import APISettings, ProjectSettings
from .log import Log


async def main():
    Log.init()

    inputs = Inputs.parse_from_args()

    project_settings = ProjectSettings()
    api_settings = APISettings(_env_file=f"{project_settings.root_dir}/.env")

    app = TranslationApp(api_settings)
    await app.start(inputs)


if __name__ == "__main__":
    asyncio.run(main())
