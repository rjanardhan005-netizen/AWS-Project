# ============================================================
# Nginx Dockerfile - Reverse Proxy
# ============================================================
# Uses the official Nginx Alpine image (very lightweight).
# Copies our custom configuration and custom error page.
# ============================================================

FROM nginx:1.25-alpine

# Remove the default Nginx config.
RUN rm /etc/nginx/conf.d/default.conf

# Copy our reverse proxy configuration.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy custom 502 error page.
COPY 502.html /usr/share/nginx/html/502.html

# Expose port 80.
EXPOSE 80
