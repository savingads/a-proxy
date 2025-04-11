FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

ENV PERSONA_API_URL=http://persona-service:5050/api/v1

EXPOSE 8123

CMD ["node", "dist/index.js"]
