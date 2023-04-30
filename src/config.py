import os
import logging
from dynaconf import Dynaconf, Validator

ROOT = os.path.dirname(__file__)

settings = Dynaconf(
    envvar_prefix="TT",
    settings_files=[
        os.path.join(ROOT, "default_settings.toml"),
        'settings.toml', 
        '.secrets.toml'
        ],
    load_dotenv=True,
    environments=True,
    default_env="default",
    validators=[
        Validator("loglevel", default="INFO", apply_default_on_none=True),
        Validator("host", default="0.0.0.0", apply_default_on_none=True),
        Validator("port", default=8080, apply_default_on_none=True),
        Validator("bot_prefix", must_exist=True, default=["/", "!"], apply_default_on_none=True),
        Validator("bot_token", must_exist=True, messages={"must_exist_true": "You forgot to set {bot_token} in your settings."}),
        Validator("bot_channel_id", must_exist=True, messages={"must_exist_true": "You forgot to set {bot_channel_id} in your settings."}),
          ]
)

#🧐LOGGING
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=settings.loglevel
)
logger = logging.getLogger(__name__)
