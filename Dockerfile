FROM alpine:latest

RUN apk update && apk upgrade apt-get install -y python3 python3-pip

# Env vars
ENV LANGUAGE="en"
ENV TELEGRAM_USERNAME ${TELEGRAM_USERNAME}
ENV TELEGRAM_CHAT_ID ${TELEGRAM_CHAT_ID}
ENV TELEGRAM_TOKEN ${TELEGRAM_TOKEN}

# set the working directory to /app
WORKDIR /app


# copy the current directory contents into the container at /app
COPY src/* /app
COPY requirements.txt /
RUN pip install -r requirements.txt

# run app.py when the container launches
CMD ["python", "bot.py"]
