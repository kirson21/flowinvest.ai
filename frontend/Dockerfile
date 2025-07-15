# Railway Dockerfile for Frontend

FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
COPY yarn.lock ./
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN yarn build

# Install serve to serve the built app
RUN yarn global add serve

# Expose port
EXPOSE 3000

# Start the application
CMD ["serve", "-s", "build", "-l", "3000"]