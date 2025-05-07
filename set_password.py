import os, sys
from configparser import ConfigParser
from werkzeug.security import generate_password_hash

if __name__ == "__main__":
    config = ConfigParser()
    FILENAME = "config.ini"
    if os.path.exists(FILENAME):
        config.read(FILENAME)
    if 'Editor' not in config.sections(): config.add_section('Editor')
    if sys.argv[-2] != 'set_password.py': raise ValueError("Введите команду в формате python3 set_password.py YOUR_PASSWORD")
    config.set('Editor', 'password', generate_password_hash(sys.argv[-1]))
    print(f"Установлен пароль редактора: {sys.argv[-1]}")
    with open(FILENAME, 'w') as f:
        config.write(f)