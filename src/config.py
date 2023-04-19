
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="TT",
    settings_files=['settings.toml', '.secrets.toml'],
    load_dotenv=True
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
