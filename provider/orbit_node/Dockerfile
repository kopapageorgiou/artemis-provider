FROM node:gallium-bullseye-slim

WORKDIR /root/orbit_api

COPY orbit_api/package*.json .
RUN npm install
COPY orbit_api/index.js .

WORKDIR /root

# If you are building your code for production
# RUN npm ci --omit=dev