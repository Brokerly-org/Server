FROM 3.9-alpine3.13

RUN pip install --upgrade pip

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY /src /user/src/app

EXPOSE 9981

CMD ["python", "/usr/src/app/main.py"]