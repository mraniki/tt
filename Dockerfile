# set base image (host OS)

FROM python:3.10

# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .
RUN pip install --upgrade pip
# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./src .

ADD /config/example.toml .

# ENV ENV_FOR_DYNACONF=default

EXPOSE 8443 8080
# command to run on container start
CMD [ "python", "./bot.py" ]
