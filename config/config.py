from dotenv import load_dotenv
import argparse
import os

def load_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ENV", "--env", default="dev", help="Environment to run the application in")
    args = parser.parse_args()

    ENV = args.env
    env_file = f".env.{ENV}"
    load_dotenv(dotenv_path=env_file)

    config = {
        "ENV": os.getenv("ENVIRONMENT"),
        "HOST": os.getenv("HOST"),
        "PORT": int(os.getenv("PORT")),
        "DEBUG": os.getenv("DEBUG"),
        "CLAUDE_API_KEY": os.getenv("CLAUDE_API_KEY"),
        "FFMPEG_BIN_PATH": os.getenv("FFMPEG_BIN_PATH"),
        "GOOGLE_CALANDER_CREDENTIAL_PATH": os.getenv("GOOGLE_CALANDER_CREDENTIAL_PATH"),
    }
    return config

config = load_config()