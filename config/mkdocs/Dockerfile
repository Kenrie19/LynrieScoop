FROM python:3.11-alpine

# Install dependencies
RUN pip install --no-cache-dir mkdocs-material

# Set working directory
WORKDIR /docs

# Copy documentation files
COPY /docs .
COPY /docs/README.md /docs/index.md

# Expose port for MkDocs
EXPOSE 8000

# Start MkDocs server with specific command line options for better debugging
# Using the config file from the new location
CMD ["sh", "-c", "mkdocs serve --config-file /config/mkdocs/mkdocs.yaml --verbose -a 0.0.0.0:8000"]
