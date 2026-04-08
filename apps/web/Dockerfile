FROM node:24.14-alpine

WORKDIR /usr/src/app

COPY package*.json ./
COPY tsconfig.json ./
COPY ./.next ./.next
COPY src ./src
COPY public ./public

RUN npm install --omit=dev

EXPOSE 3000
CMD ["npm", "run", "dev"]
