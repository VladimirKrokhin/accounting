from accounts.entrypoints.sanic_app import app

__all__ = ["app"]


def start_app():
    app.run()


if __name__ == "__main__":
    start_app()
