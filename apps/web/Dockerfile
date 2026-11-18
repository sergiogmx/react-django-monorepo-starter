# Build context is the repo root (see docker-compose.yml) so npm workspaces resolve.
FROM node:22-slim

WORKDIR /app

COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/
COPY apps/docs/package.json apps/docs/
COPY packages/ui/package.json packages/ui/
COPY packages/tokens/package.json packages/tokens/
RUN npm ci

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--workspace", "apps/web", "--", "--host", "0.0.0.0"]
