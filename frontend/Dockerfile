# ============================================================
# Frontend Dockerfile - React Application (Multi-Stage Build)
# ============================================================
# Stage 1 ("build"): Installs dependencies and builds the
#   optimized production bundle using `npm run build`.
#
# Stage 2 ("production"): Uses a lightweight Node image with
#   the `serve` package to serve the static files on port 3000.
#
# Why multi-stage?
#   - The final image is much smaller because it doesn't
#     include node_modules or build tools.
#   - Only the compiled static files are in the final image.
# ============================================================

# ---- Stage 1: Build ----
FROM node:18-alpine AS build

WORKDIR /app

# Copy dependency files first for better Docker layer caching.
COPY package.json ./

# Install all dependencies (including devDependencies for build).
RUN npm install

# Copy source code and build the production bundle.
COPY . .
RUN npm run build

# ---- Stage 2: Production ----
FROM node:18-alpine AS production

WORKDIR /app

# Install 'serve' — a simple static file server.
RUN npm install -g serve@14

# Copy only the build output from Stage 1.
COPY --from=build /app/build ./build

# Serve on port 3000.
EXPOSE 3000

# Start the static file server.
CMD ["serve", "-s", "build", "-l", "3000"]
