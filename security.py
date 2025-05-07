import os, secrets
from configparser import ConfigParser
from werkzeug.security import generate_password_hash, check_password_hash

CONFIG_FILE = "config.ini"

if not os.path.exists(CONFIG_FILE):
    raise FileExistsError(f"Отсутствует файл {CONFIG_FILE}.\n"
                          "Если вы клонировали или запуллили git-репозиторий, настройте "
                          "пароль редактора командой `python set_password.py YOUR_PASSWORD`.")
__config = ConfigParser()
__config.read(CONFIG_FILE)
if not (__config.has_section("Editor") and __config.has_option("Editor", "password")):
    raise FileExistsError(f"В файле {CONFIG_FILE} отсутствует настройка пароля редактора.\n"
                          "Настройте пароль редактора командой `python set_password.py YOUR_PASSWORD`.")
EDITOR_PASSWORD_HASH = __config.get('Editor', 'password')

if not __config.has_section("General"): __config.add_section('General')
if not __config.has_option('General', 'flask_secret_key'):
    __config.set('General', 'flask_secret_key', secrets.token_hex())
    with open(CONFIG_FILE, 'w') as f:
        __config.write(f)
FLASK_SECRET_KEY = __config.get('General', 'flask_secret_key')

def check_password(password: str):
    return check_password_hash(EDITOR_PASSWORD_HASH, password)
