import os

from pyaml_env import parse_config


config = parse_config(os.environ.get('APP_CONFIG', './config.yaml'))
