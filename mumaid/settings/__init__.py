
import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

ENVIRONMENT = env("ENVIRONMENT", default="dev")

print(f"Running in {ENVIRONMENT} environment")  

if ENVIRONMENT == "prod":
    from .prod import *
else:
    from .dev import *