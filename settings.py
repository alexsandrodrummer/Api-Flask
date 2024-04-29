from app import app  # Importa o objeto app do módulo app
from dynaconf import Dynaconf

# Configurações usando Dynaconf
settings = Dynaconf(
    app,  # Objeto app do Flask
    settings_files=["settings.toml", "secrets.toml"],  # Arquivos de configuração
)
