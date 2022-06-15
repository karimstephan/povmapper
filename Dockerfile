FROM --platform=linux/x86_64 python:3.8.12-buster

COPY api /api
COPY povmapper /povmapper
COPY requirements.txt /requirements.txt
#COPY /Users/cherifbenham/code/keys/povertymapper-829ba3762637.json /credentials.json

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD uvicorn api.fast:app --host 0.0.0.0 --port $PORT