# Build stage
FROM node:20-alpine as build

WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the site with 11ty
RUN npx @11ty/eleventy

# Production stage with Nginx
FROM nginx:stable-alpine

# Copy built static files from the build stage to Nginx serve directory
COPY --from=build /app/_site /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
