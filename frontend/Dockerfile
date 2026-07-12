FROM node:20-slim AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
ENV BACKEND_URL=http://backend:8000
RUN npm run build

FROM node:20-slim
WORKDIR /app
ENV NODE_ENV=production
ENV BACKEND_URL=http://backend:8000
COPY --from=build /app/.next ./.next
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/next.config.js ./next.config.js
EXPOSE 3000
CMD ["npm", "start"]
