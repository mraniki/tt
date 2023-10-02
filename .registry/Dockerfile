FROM python:3.11
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV


ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV ENV_FOR_DYNACONF=default
ENV OP_SERVICE_ACCOUNT_TOKEN=NONE
ENV OP_VAULT=NONE
ENV OP_ITEM=NONE
ENV TT_DOCKER=True

COPY . /app
RUN pip install --no-cache-dir /app

EXPOSE 8080
HEALTHCHECK --interval=5s CMD curl --fail http://localhost:8080 || exit 1

CMD [ "python", "/app/tt/app.py" ]




# RUN apt-get update && \
# apt-get -y install chromium && \
#   pip install -U pip && \
#   pip install playwright && \
#   playwright install chromium && playwright install-deps && \
#   rm -rf /var/lib/apt/lists/*