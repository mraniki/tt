FROM python:3.11
WORKDIR /app
COPY ./src/bot.py ./src/config.py ./src/requirements.txt ./src/default_settings.toml .
COPY ./src/example.env .env
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD [ "python", "./bot.py" ]
