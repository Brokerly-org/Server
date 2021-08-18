@echo off
cls
if not exist "mkcert.exe" (
    start "" https://github.com/FiloSottile/mkcert/releases/latest
    echo please download mkcert.exe and rename it to mkcert.exe
    pause
    exit 1
)

mkcert -install
mkcert localhost 127.0.0.1 ::1
move localhost+2-key.pem key.pem
move localhost+2.pem cert.pem