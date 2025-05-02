FROM node:21-slim AS builder

RUN mkdir ./app
WORKDIR ./app

COPY ./frontend/* .
COPY ./frontend/public ./public
COPY ./frontend/src ./src
COPY ./frontend/nginx ./nginx

RUN npm ci
RUN npm run build

FROM nginx:1.23.1

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/*

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built app and nginx conf
COPY --from=builder ./app/dist/ /usr/share/nginx/html
COPY --from=builder ./app/nginx/nginx.conf /etc/nginx/conf.d

CMD ["nginx", "-g", "daemon off;"]