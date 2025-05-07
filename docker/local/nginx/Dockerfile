FROM nginx:1.27.0-alpine3.19-slim

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom NGINX config
COPY ./nginx.conf /etc/nginx/conf.d/default.conf