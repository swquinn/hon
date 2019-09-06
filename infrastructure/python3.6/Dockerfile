#:
FROM python:3.6

ENV CHECKOUT_DIR=/usr/src/hon

COPY . $CHECKOUT_DIR
COPY ./infrastructure/github-build.sh /github-build.sh
RUN chmod +x /github-build.sh

WORKDIR $CHECKOUT_DIR