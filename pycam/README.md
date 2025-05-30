# PyCAM - Photo Editor

![PyCAM Logo](pycam_header.jpeg)

## Overview

PyCAM is a modern, web-based photo editing application that allows users to easily upload, edit, and share their images. It offers a user-friendly interface with real-time effects and a personal gallery.

## Features

- **Simple Upload**: Drag and drop or select images from your device
- **Real-time Effects**: Apply various effects to your images:
  - Brightness adjustment
  - Contrast enhancement
  - Grayscale conversion
  - Sepia tone
  - Blur effects
  - Color inversion
  - Saturation adjustment
- **Personal Gallery**: Save edited images to your personal gallery
- **Sharing Options**: Easily share your creations:
  - Download in high quality
  - Share to Facebook
  - Share to Instagram
  - (More platforms coming soon)
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

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


















