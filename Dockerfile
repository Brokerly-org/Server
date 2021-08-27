FROM python:3.9-alpine3.13

WORKDIR /usr/src/app

RUN apk add --no-cache gcc python3-dev musl-dev alpine-sdk

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

ENV IS_PRODUCTION=TRUE

COPY /src ./

EXPOSE 9981

CMD ["python", "./main.py"]