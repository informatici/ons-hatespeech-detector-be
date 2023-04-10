import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', "b54345b8bc07839e82a0e01e1e883de8d360c338d6f56edcde30e2e273f6ab24")
DEFAULT_USER = os.getenv('DEFAULT_USER', None)
DEFAULT_PASSWORD = os.getenv('DEFAULT_PASSWORD', None)
SIGNUP_ENABLED = os.getenv('SIGNUP_ENABLED', False)

# Minimal check for sanity
if len(DEFAULT_USER)<1: del DEFAULT_USER
if len(DEFAULT_PASSWORD)<1: del DEFAULT_PASSWORD
