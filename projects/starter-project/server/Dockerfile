# Proxy server (Node.js / Express) - production image
FROM node:20-alpine

ENV NODE_ENV=production \
    PORT=3001

WORKDIR /app

# Install production deps first for layer caching
COPY package*.json ./
RUN npm ci --omit=dev

COPY server.js ./

# server.js reads agent definitions from ../.claude/agents at runtime.
# Mount or copy that directory to /.claude/agents (see docker-compose.yml).
RUN apk add --no-cache curl \
    && addgroup -g 1001 -S nodejs \
    && adduser -S nodejs -u 1001
USER nodejs

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/api/health" || exit 1

CMD ["node", "server.js"]
