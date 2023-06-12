FROM python:3.11
WORKDIR /app
COPY ./tt .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD [ "python", "./bot.py" ]
