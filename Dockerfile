FROM python:3.9-alpine3.13

WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY /src ./

EXPOSE 9981

CMD ["python", "./main.py"]