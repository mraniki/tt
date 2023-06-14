FROM python:3.11-slim
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . /app
RUN pip install --no-cache-dir install /app
#or RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
#ENV PYTHONPATH /app
CMD [ "python", "/app/tt/bot.py" ]
