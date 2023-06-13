FROM python:3.11

COPY tt/ /tt/
COPY pyproject.toml .
RUN pip install -e tt
WORKDIR /tt
# RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD [ "python", "bot.py" ]

