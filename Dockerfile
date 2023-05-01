FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./src .
EXPOSE 8443 8080
CMD [ "python", "./bot.py" ]