#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Replace environment variables in the Nginx configuration template
# and save the output to the actual Nginx configuration file
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf

# Start Nginx in the foreground (no daemon mode)
nginx -g 'daemon off;'
