FROM python:3.9-slim-buster

LABEL maintainer="Tonye Jack <jtonye@ymail.com>"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]