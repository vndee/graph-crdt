FROM python:3.8-slim-buster

WORKDIR /graph_crdt
ENV PYTHONPATH "${PYTHONPATH}:/graph_crdt"

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh
CMD ./entrypoint.sh $ADDRESS $FRIEND_ADDRESS
