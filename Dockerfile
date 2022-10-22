FROM alpine:latest

RUN apk update && apk upgrade 
RUN apk add --no-cache python3 py3-pip \
		&& pip3 install --upgrade pip 

# Env vars
ENV LANGUAGE="en"
ENV TELEGRAM_USERNAME ${TELEGRAM_USERNAME}
ENV TELEGRAM_CHAT_ID ${TELEGRAM_CHAT_ID}
ENV TELEGRAM_TOKEN ${TELEGRAM_TOKEN}

# set the working directory to /app
WORKDIR /app


# copy the current directory contents into the container at /app
COPY /src /app
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# run app.py when the container launches
CMD ["python", "bot.py"]
