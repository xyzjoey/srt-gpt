from argparse import ArgumentParser

from pydantic import BaseModel


class CommandInputs(BaseModel):
    class Config:
        allow_population_by_field_name = True

    @classmethod
    def add_arguments(cls, parser):
        for field_name, field in cls.__fields__.items():
            help = field.field_info.description or ""
            if field.required:
                parser.add_argument(field_name, help=help)
            else:
                arg_names = [f"--{field_name}"]
                if field.has_alias:
                    arg_names.append(f"--{field.alias}")
                parser.add_argument(*arg_names, help=f"{help}\ndefault={field.default}", default=field.default)

    @classmethod
    def parse_from_args(cls):
        parser = ArgumentParser("srt_helper")

        cls.add_arguments(parser)

        args = parser.parse_args()
        return cls(**args.__dict__)
