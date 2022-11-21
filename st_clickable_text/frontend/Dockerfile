FROM node:12-slim

ARG NODE_ENV=development

ENV NODE_PATH=/srv/app/node_modules
WORKDIR /srv/app
COPY package.json .env .prettierrc tsconfig.json public ./
#COPY yarn.lock ./

RUN set -ex; \
  if [ "$NODE_ENV" = "production" ]; then \
    yarn install --no-cache --frozen-lockfile --production; \
  else \
    yarn install --no-cache --frozen-lockfile; \
  fi;

COPY . /srv/app

CMD ["yarn", "start"]
