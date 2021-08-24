from uvicorn import run

from core.settings import Settings


settings = Settings()

DEBUG = True if not settings.is_production else False


def main():
    run("api:app", host="0.0.0.0", port=9981, debug=DEBUG)


if __name__ == "__main__":
    main()
