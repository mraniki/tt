FROM python:3.11-slim
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV ENV_FOR_DYNACONF=DEFAULT
#TODO IMPORT .env example file to centralize all env variables

COPY . /app
RUN pip install --no-cache-dir install /app
EXPOSE 8080

CMD [ "python", "/app/tt/bot.py" ]
