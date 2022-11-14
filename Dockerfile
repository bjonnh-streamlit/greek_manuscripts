FROM python:3.10

RUN pip install --upgrade pip

RUN useradd -m python
RUN mkdir /src /data && chown python /src /data
RUN apt update && apt -y install antiword
USER python
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

