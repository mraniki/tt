# set base image (host OS)
FROM python:latest

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./src .

#Telegram bot token 
ENV TELEGRAM_TOKEN="" 
#TG user for bot control
ENV TELEGRAM_ALLOWED_USER_ID=""

#CCXT supported exchange details

#CCXT SANDBOX details
ENV TEST_SANDBOX_MODE="True"
ENV TEST_SANDBOX_EXCHANGE_NAME="binance"
ENV TEST_SANDBOX_YOUR_API_KEY="" 
ENV TEST_SANDBOX_YOUR_SECRET=""
ENV TEST_SANDBOX_ORDERTYPE="market"

#PROD APIKEY Exchange1
ENV EXCHANGE1_NAME="binance"
ENV EXCHANGE1_YOUR_API_KEY=""
ENV EXCHANGE1_YOUR_SECRET=""
ENV EXCHANGE1_ORDERTYPE="market" 

# command to run on container start
CMD [ "python", "./bot.py" ]
