# set base image (host OS)

FROM python:3.7

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./src .

RUN mkdir ./config
ADD ./config/db.json.sample ./config/db.json.sample
ADD ./config/env.sample ./config/env.sample

# command to run on container start
CMD [ "python", "./bot.py" ]
