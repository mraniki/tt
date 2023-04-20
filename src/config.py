
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="TT",
    settings_files=['settings.toml', '.secrets.toml','example.toml'],
    load_dotenv=True,
    environments=True,
    default_env="default",
)
