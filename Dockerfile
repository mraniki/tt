FROM alpine:latest

RUN apk update && apk upgrade

# Env vars
ENV LANGUAGE="en"
ENV TELEGRAM_USERNAME ${TELEGRAM_USERNAME}
ENV TELEGRAM_ID ${TELEGRAM_ID}
ENV TELEGRAM_HASH ${TELEGRAM_HASH}


# set the working directory to /app
WORKDIR /app

# copy the current directory contents into the container at /app
COPY . /app


RUN git clone https://github.com/mraniki/tt /app
COPY /src /src

COPY requirements.txt .
RUN pip3 install -r requirements.txt

# run app.py when the container launches
CMD ["python", "bot.py"]
