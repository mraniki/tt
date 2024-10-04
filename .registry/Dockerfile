FROM python:3.11


##
# Environment variables
#
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV TT_DOCKER=True
ENV ENV_FOR_DYNACONF=default
ENV OP_PATH=/usr/bin/op
ENV OP_SERVICE_ACCOUNT_TOKEN=""
ENV OP_VAULT = ""
ENV OP_ITEM = ""

##
# Install Interative Brokers Gateway
#
# RUN wget -q https://github.com/IbcAlpha/IBC/releases/download/3.18.0-Update.1/IBCLinux-3.18.0.zip -O ibc.zip \
#   && sha256sum -c ibc.zip.sha256 \
#   && unzip ibc.zip -d /opt/ibc \
#   && chmod o+x /opt/ibc/*.sh /opt/ibc/*/*.sh \
#   && rm ibc.zip \
#   && apt-get clean \

##
# Install playwright
##
RUN apt-get update && \
  apt-get -y install chromium xvfb && \
  pip install -U pip && \
  pip install playwright && \
  playwright install chromium && playwright install-deps && \
  rm -rf /var/lib/apt/lists/*

##
# Install 1Password CLI
##
RUN wget -P /tmp/ https://downloads.1password.com/linux/debian/$(dpkg --print-architecture)/stable/1password-cli-$(dpkg --print-architecture)-latest.deb
RUN dpkg -i /tmp/1password-cli-$(dpkg --print-architecture)-latest.deb
RUN op --version

##
# Deploy app
#
WORKDIR /app
COPY . /app
# RUN pip install --no-cache-dir /app
RUN pip install --no-deps /app
##
# Healthcheck and PORT
#
EXPOSE 8080
HEALTHCHECK --interval=5s CMD curl --fail http://localhost:8080 || exit 1

##
# Run app
#
CMD [ "xvfb-run", "python", "/app/tt/app.py" ]


