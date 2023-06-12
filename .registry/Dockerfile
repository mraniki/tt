FROM python:3.11
COPY tt/ /tt/
RUN ls --recursive /tt/
WORKDIR /tt
# COPY ./tt .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD [ "python", "bot.py" ]
