FROM python:3.11
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV ENV_FOR_DYNACONF=default

RUN apt-get update && \
apt-get -y install chromium && \
  pip install -U pip && \
  pip install playwright && \
  playwright install && playwright install-deps && \
  rm -rf /var/lib/apt/lists/*

ENV OP_SERVICE_ACCOUNT_TOKEN=NONE
COPY --from=1password/op:2 /usr/local/bin/op /usr/local/bin/op

COPY . /app
RUN pip install --no-cache-dir install /app
EXPOSE 8080

CMD [ "python", "/app/tt/bot.py" ]
