FROM python:3.11-slim
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV ENV_FOR_DYNACONF=default

COPY --from=1password/op:2 /usr/local/bin/op /usr/local/bin/op

COPY . /app
RUN pip install --no-cache-dir install /app
EXPOSE 8080

CMD [ "python", "/app/tt/bot.py" ]
