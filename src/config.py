
from dynaconf import Dynaconf, Validator



settings = Dynaconf(
    envvar_prefix="TT",
    settings_files=['settings.toml', '.secrets.toml'],#,'example.toml'],
    load_dotenv=True,
    environments=True,
    default_env="default",
    validators=[
        Validator("loglevel", default="INFO", apply_default_on_none=True),
        Validator("host", default="0.0.0.0", apply_default_on_none=True),
        Validator("port", default=8080, apply_default_on_none=True),
        Validator("bot_token", must_exist=True, messages={"must_exist_true": "You forgot to set {bot_token} in your settings."}),
        Validator("bot_channel_id", must_exist=True, messages={"must_exist_true": "You forgot to set {bot_channel_id} in your settings."}),
       # Validator("identifier", default=["BUY", "SELL", "buy", "sell","Buy","Sell"],apply_default_on_none=True),
          ]
)


# #🧐LOGGING
# logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=settings.loglevel)
# logger = logging.getLogger(__name__)
# if settings.loglevel=='DEBUG':
#     logging.getLogger('ccxt').setLevel(logging.WARNING)
#     logging.getLogger('urllib3').setLevel(logging.WARNING)
#     logging.getLogger('telegram').setLevel(logging.WARNING)
#     logging.getLogger('apprise').setLevel(logging.WARNING)
#     logging.getLogger('telethon').setLevel(logging.WARNING)
#     logging.getLogger('discord').setLevel(logging.WARNING)
#     logging.getLogger('simplematrixbotlib').setLevel(logging.WARNING)