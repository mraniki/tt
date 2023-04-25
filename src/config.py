
from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="TT",
    settings_files=['findmyorder/default_settings.toml','settings.toml', '.secrets.toml'],#,'example.toml'],
    load_dotenv=True,
    environments=True,
    default_env="default",
    validators=[
        Validator("loglevel", default="INFO", apply_default_on_none=True),
        Validator("host", default="0.0.0.0", apply_default_on_none=True),
        Validator("port", default=8080, apply_default_on_none=True),
        Validator("bot_token", must_exist=True, messages={"must_exist_true": "You forgot to set {bot_token} in your settings."}),
        Validator("bot_channel_id", must_exist=True, messages={"must_exist_true": "You forgot to set {bot_channel_id} in your settings."}),
          ]
)
