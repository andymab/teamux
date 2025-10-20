ARG NODE_BASE=mirror.gcr.io/library/node:20-alpine
FROM ${NODE_BASE}
WORKDIR /app
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then \
      npm ci --no-audit --no-fund; \
    else \
      npm install --no-audit --no-fund; \
    fi
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
