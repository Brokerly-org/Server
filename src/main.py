from uvicorn import run

from core.settings import get_settings


def main():
    settings = get_settings()
    run("server:app", host=settings.host, port=settings.port, debug=(not settings.is_production))


if __name__ == "__main__":
    main()
