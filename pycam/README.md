# PyCam

A Django-based web application for photo editing.

## Features
- Photo editing tools
- User accounts
- Cloud storage integration

## Deployment
This application is configured for deployment on Render.com.

## Overview

PyCAM is a modern, web-based photo editing application that allows users to easily upload, edit, and share their images. It offers a user-friendly interface with real-time effects and a personal gallery.

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python with Django framework
- **Image Processing**: PIL/Pillow for server-side processing

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pycam.git
   cd pycam
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

6. Visit `http://localhost:8080/` in your browser

## Usage

1. **Upload an Image**: Click on the upload area or drag an image
2. **Apply Effects**: Select from the effects panel to preview changes
3. **Save Edited Image**: Click the Save button to add to your gallery
4. **Share Your Creation**: Open the gallery and use the sharing options

## Browser Compatibility

PyCAM works with all modern browsers including:
- Chrome
- Firefox
- Safari
- Edge

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Font Awesome](https://fontawesome.com/) for icons
- [Bootstrap](https://getbootstrap.com/) for UI components
- All the contributors who helped build PyCAM

Based on your screenshots of the Render dashboard, here's what you should fill in each field:

**Language:**
- Keep as "Python 3"

**Branch:**
- Keep as "main" (or whatever branch has your code)

**Region:**
- Keep as "Oregon (US West)" is fine

**Root Directory:**
- Leave empty since your application is in the root of your repository

**Build Command:**
- Replace with: `./build.sh`

**Start Command:**
- Replace with: `cd pycam && gunicorn pycam.wsgi:application --bind 0.0.0.0:$PORT --config gunicorn_config.py`

**Instance Type:**
- For hobby/testing: Choose "Free" tier
- For production: Select based on your needs (Pro or higher recommended for real users)

**Environment Variables:**
Click "Add Environment Variable" and add these key-value pairs:
- `DJANGO_SETTINGS_MODULE`: `pycam.render_settings`
- `SECRET_KEY`: (Generate a random string or click "Generate" button)
- `ENVIRONMENT`: `production`
- `WEB_CONCURRENCY`: `4`
- `THREADS_PER_WORKER`: `4`
- `CLOUDINARY_CLOUD_NAME`: (Your Cloudinary cloud name)
- `CLOUDINARY_API_KEY`: (Your Cloudinary API key)
- `CLOUDINARY_API_SECRET`: (Your Cloudinary API secret)

The database connection string will be automatically added if you create a database in Render.
