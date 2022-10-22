FROM python:3

RUN apt update && apt install -

# Env vars
ENV TELEGRAM_USERNAME ${TELEGRAM_USERNAME}
ENV TELEGRAM_CHAT_ID ${TELEGRAM_CHAT_ID}
ENV TELEGRAM_TOKEN ${TELEGRAM_TOKEN}

COPY /src /
RUN pip3 install --no-cache-dir -r requirements.txt

# run app.py when the container launches
CMD ["python bot.py"]
