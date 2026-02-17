from dotenv import find_dotenv, load_dotenv
from accounts.entrypoints.sanic_app import create_app

__all__ = ["app", "start_app"]

app = create_app()


def start_app():
    env_file = find_dotenv(".env.production")
    load_dotenv(env_file)
    app.run()


if __name__ == "__main__":
    start_app()
