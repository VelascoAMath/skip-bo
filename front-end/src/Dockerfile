FROM node

WORKDIR /usr/src/app


COPY ./package.json ./
COPY ./package-lock.json ./

RUN npm install

COPY ./src ./
COPY ./public ./

EXPOSE 3000


CMD ["npm", "start"]


