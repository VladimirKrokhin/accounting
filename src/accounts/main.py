from accounts.entrypoints.sanic_app import create_app

__all__ = ["app", "start_app"]

app = create_app(read_dotenv=True)


def start_app():
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start_app()
