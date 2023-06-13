FROM python:3.11-slim
WORKDIR /app
#COPY tt/ /app/tt/
COPY . /app
WORKDIR /app/tt/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
ENV PYTHONPATH /app
CMD [ "python", "/app/tt/bot.py" ]

#TODO 
#FROM python:3.11-slim
#RUN python -m venv /opt/venv
#EXPOSE 8080

#WORKDIR /app
#COPY . /app

#RUN . /opt/venv/bin/activate && pip install /app
#OR
#COPY ./requirements/requirements.txt .
#RUN . /opt/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Run the application:
#CMD . /opt/venv/bin/activate && exec python /app/tt/bot.py


#
#ENV VIRTUAL_ENV=/opt/venv
#RUN python3 -m venv $VIRTUAL_ENV
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
#COPY requirements.txt .
#RUN pip install -r requirements.txt

# Run the application:
#COPY myapp.py .
#CMD ["python", "myapp.py"]