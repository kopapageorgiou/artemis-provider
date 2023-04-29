FROM node:gallium-bullseye-slim

WORKDIR /root/orbit_api

COPY orbit_api/package*.json .
COPY orbit_api/index.js .
RUN npm install

WORKDIR /root

# If you are building your code for production
# RUN npm ci --omit=dev