FROM python:3.11
RUN python3 -m venv $VIRTUAL_ENV

##
# Environment variables
#

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV TT_DOCKER=True
ENV ENV_FOR_DYNACONF=default
ENV OP_PATH=/usr/bin/op
ENV OP_SERVICE_ACCOUNT_TOKEN=None
ENV OP_COMMAND="op read op://OP_VAULT/OP_ITEM/notesPlain > .op.toml"

##
# Install 1Password CLI
#
RUN wget -P /tmp/ https://downloads.1password.com/linux/debian/$(dpkg --print-architecture)/stable/1password-cli-$(dpkg --print-architecture)-latest.deb
RUN dpkg -i /tmp/1password-cli-$(dpkg --print-architecture)-latest.deb
RUN op --version

##
# Deploy app
#
COPY . /app
RUN pip install --no-cache-dir /app

##
# Healthcheck and PORT
#
EXPOSE 8080
HEALTHCHECK --interval=5s CMD curl --fail http://localhost:8080 || exit 1

##
# Run app
#
CMD [ "python", "/app/tt/app.py" ]



# RUN apt-get update && \
# apt-get -y install chromium && \
#   pip install -U pip && \
#   pip install playwright && \
#   playwright install chromium && playwright install-deps && \
#   rm -rf /var/lib/apt/lists/*
