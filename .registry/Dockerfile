FROM python:3.10
WORKDIR /app
COPY ./src/bot.py ./src/config.py ./src/requirements.txt ./src/default_settings.toml .
COPY ./src/example.env .env
RUN pip install -r requirements.txt
EXPOSE 8080
CMD [ "python", "./bot.py" ]