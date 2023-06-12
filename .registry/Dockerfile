FROM python:3.11
COPY tt/ /tt/
WORKDIR /tt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD [ "python", "-m", "tt.bot" ]
