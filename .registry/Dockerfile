FROM python:3.11
WORKDIR /app
COPY tt/ /app/tt/
WORKDIR /app/tt/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
ENV PYTHONPATH /app
CMD [ "python", "/app/tt/bot.py" ]
