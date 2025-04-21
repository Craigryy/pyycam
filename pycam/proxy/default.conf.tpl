server {
    listen ${LISTEN_PORT};
    

    # Static files
    location /static/static {
        alias /vol/static;
    }

    # Media files
    location /static/media {
        alias /vol/media;
    }

    # Forward all other requests to the application
    location / {
        include              gunicorn_headers;
        proxy_redirect       off;
        proxy_pass           http://${APP_HOST}:${APP_PORT};
        client_max_body_size 10M;  # Limit the size of client requests
    }
}
