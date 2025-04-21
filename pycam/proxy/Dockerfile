# Use the official lightweight Nginx Alpine image as the base image
FROM nginx:1-alpine

# Set the maintainer label to indicate who is responsible for the image
LABEL maintainer="Harrison James"

# Copy the Nginx configuration template into the container
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl

# Copy custom headers configuration for Gunicorn requests
COPY ./gunicorn_headers /etc/nginx/gunicorn_headers

# Copy the custom startup script that will configure Nginx before launch
COPY ./run.sh /run.sh

# Set environment variables for dynamic configuration
ENV LISTEN_PORT=5000     
ENV APP_HOST=app        
ENV APP_PORT=9000       

# Set the user to root for modifying necessary directories
USER root

# Create necessary directories for static files, set permissions 
#Create a directory for static files
# Set proper permissions
# Change ownership to Nginx user
# Ensure the config file exists
# Set ownership
RUN mkdir -p /vol/static && \                  
    mkdir -p /vol/media && \                   
    chmod -R 755 /vol && \                    
    chown -R nginx:nginx /vol && \             
    touch /etc/nginx/conf.d/default.conf && \  
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \ 
    chmod +x /run.sh  # Make the run script executable

# Define volumes to persist static and media files even when the container restarts
VOLUME /vol/static
VOLUME /vol/media

# Run the startup script when the container launches
CMD ["/run.sh"]
