FROM python:3

WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

ENV IS_PRODUCTION=TRUE

COPY /src ./

EXPOSE 9981

CMD ["python", "./main.py"]