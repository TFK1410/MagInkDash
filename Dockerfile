FROM python:3.10-alpine

WORKDIR /app

RUN apk add --no-cache ca-certificates git
RUN git clone https://github.com/TFK1410/MagInkDash .

RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]