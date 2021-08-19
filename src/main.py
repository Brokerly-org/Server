from uvicorn import run
from dotenv import load_dotenv
from os import environ

load_dotenv()
PRODUCTION = environ.get('APP_ENV') == 'production'
DEBUG = True if not PRODUCTION else False

def main():
    run("api:app", host="0.0.0.0", port=9981, debug=DEBUG) # ssl_keyfile="..\https_cert\key.pem", ssl_certfile="..\https_cert\cert.pem")

if __name__ == "__main__":
    main()
