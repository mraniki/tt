# set base image (host OS)
FROM python:3.6

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./src .

# set the token for the telegram bot
ENV TOKEN=""
##from @RawDataBot
ENV ALLOWED_USER_ID="" 

##from EXCHANGE to CONNECT
ENV EXCHANGE1="binance"
ENV EXCHANGE1YOUR_API_KEY="YOURAPI"
ENV EXCHANGE1YOUR_SECRET="YOURSECRET"

# command to run on container start
CMD [ "python", "./bot.py" ]
