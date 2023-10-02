FROM python:3.11
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# ARG BRANCH_NAME
# ENV BRANCH=$BRANCH_NAME
ENV TT_DOCKER=True

ENV ENV_FOR_DYNACONF=default
ENV OP_SERVICE_ACCOUNT_TOKEN=None
ENV OP_VAULT=None
ENV OP_ITEM=None

COPY --from=1password/op:2 /usr/local/bin/op /usr/local/bin/op
RUN op read op://$OP_VAULT/$OP_ITEM/notesPlain > .op.toml

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