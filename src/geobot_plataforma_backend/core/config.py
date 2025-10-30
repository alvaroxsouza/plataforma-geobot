"""
Configuração centralizada usando Dynaconf
"""
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="GEOBOT",
    settings_files=['settings.toml', 'settings.local.toml', '.secrets.toml', '.secrets.local.toml'],
    environments=True,
    load_dotenv=True,
    env_switcher="GEOBOT_ENV",
    merge_enabled=True,
)

# Para garantir que o settings pode ser importado facilmente
__all__ = ['settings']

