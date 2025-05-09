import os, sys
from configparser import ConfigParser

if __name__ == "__main__":
    config = ConfigParser()
    FILENAME = "config.ini"
    if os.path.exists(FILENAME):
        config.read(FILENAME)
    if not config.has_section('General'): config.add_section('General')
    if sys.argv[-2] != 'production.py': raise ValueError("Введите команду в формате python3 production.py [true|false]")
    is_production = (sys.argv[-1].lower() == "true")
    config.set('General', 'production', str(is_production))
    print(f"Выбран режим релиза" if is_production else f"Выбран режим разработки")
    with open(FILENAME, 'w') as f:
        config.write(f)