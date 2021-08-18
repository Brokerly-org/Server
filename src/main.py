from uvicorn import run


def main():
    run("api:app", host="0.0.0.0", port=9981) # ssl_keyfile="..\https_cert\key.pem", ssl_certfile="..\https_cert\cert.pem")

if __name__ == "__main__":
    main()
