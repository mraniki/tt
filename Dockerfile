# set base image (host OS)

FROM python:3.10

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./src .

RUN mkdir /code/config
ADD /config/sample_db.json /code/config/sample_db.json
EXPOSE 8443
EXPOSE 8080
# command to run on container start
CMD [ "python", "./bot.py" ]

HEALTHCHECK CMD ps aux | grep 'python ./bot.py' || exit 1