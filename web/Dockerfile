FROM node:9-alpine

COPY ./web/package.json /app/web/package.json
COPY ./web/yarn.lock /app/web/yarn.lock

WORKDIR /app/web/

RUN yarn