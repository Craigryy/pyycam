from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import close_old_connections, connection
from .models import ImageEdit
from .forms import ImageEditForm
from .effects import apply_effect
import base64
import io
import json
from PIL import Image
import logging
import time

# Set up logging
logger = logging.getLogger(__name__)

def login_view(request):
    """Simple login page that redirects authenticated users"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'login.html')

def homepage(request):
    """Homepage with editor and gallery - requires login"""
    if not request.user.is_authenticated:
        return redirect('login_page')

    # Get user's images for the gallery
    images = ImageEdit.objects.filter(user=request.user).order_by('-created_at')
    form = ImageEditForm()

    return render(request, 'homepage.html', {
        'images': images,
        'form': form,
    })

@login_required
@require_POST
def apply_image_effect(request):
    """Apply image effects and return processed image preview"""
    #Implement to debug to know if there is an error , reason is because we want to make sure the request is coming from the frontend
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':#this is a check to see if the request is an AJAX request,reason is because we want to make sure the request is coming from the frontend
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})#this is a response to the request if it is not an AJAX request

    try:
        # Get request data
        effect_name = request.POST.get('effect')
        image_data = request.POST.get('image')


        if not effect_name or not image_data:
            return JsonResponse({'status': 'error', 'message': 'Missing effect or image data'})

        # Extract image data from base64
        format, imgstr = image_data.split(';base64,')#note the image data is long and has a ;base64, at the end, so we need to split it
        # Get the file extension
        ext = format.split('/')[-1]#this is the file extention needed "e.g - jpg, png, etc."
        # Decode the image data
        img_data = base64.b64decode(imgstr)#this is the image data in bytes
        # Open the image
        img = Image.open(io.BytesIO(img_data))#this is the image object, reason is python can manage the image data in bytes and manipulate it

        # Log basic info - helps me debug
        logger.info(f"Processing {effect_name} effect on {img.size} image")

        # Process image with selected effect
        processed_image = apply_effect(img, effect_name)
        if processed_image.mode != 'RGB':
            processed_image = processed_image.convert('RGB')

        # Return processed image as base64
        image_data = io.BytesIO()
        processed_image.save(image_data, format=ext.upper())
        img_str = base64.b64encode(image_data.getvalue()).decode('utf-8')

        return JsonResponse({
            'status': 'success',
            'image': f'data:image/{ext};base64,{img_str}',
            'effect': effect_name
        })

    except Exception as e:
        logger.error(f"Error applying effect: {str(e)}")
        return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})

@login_required
@require_POST
def save_image(request):
    """Save edited image to user's gallery - supports both form and AJAX methods"""
    # Debug to know if there is an error , reason is because we want to make sure the request is coming from the frontend
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    logger.info(f"Save image request: {'AJAX' if is_ajax else 'form'}")

    try:
        # Handle regular form upload
        if 'original_image' in request.FILES:#this is a check to see if the request has an original image
            form = ImageEditForm(request.POST, request.FILES)
            if form.is_valid():
                # Create and save the image edit
                image_edit = form.save(commit=False)
                image_edit.user = request.user
                effect_applied = request.POST.get('effect_applied', '')
                image_edit.effect_applied = effect_applied

                # Process with effect if one was selected
                if effect_applied and effect_applied != 'original':
                    original_img = Image.open(request.FILES['original_image'])
                    processed_img = apply_effect(original_img, effect_applied)

                    # Save both original and processed images
                    image_edit.save()

                    # Save processed image to edited_image field
                    buffer = io.BytesIO()
                    img_format = 'JPEG' if request.FILES['original_image'].name.lower().endswith('.jpg') else 'PNG'
                    processed_img.save(buffer, format=img_format)

                    timestamp = int(time.time())
                    filename = f"edited_{request.user.id}_{effect_applied}_{timestamp}.{img_format.lower()}"
                    image_edit.edited_image.save(filename, ContentFile(buffer.getvalue()))
                else:
                    # No effect - just use original
                    image_edit.edited_image = image_edit.original_image
                    image_edit.save()

                messages.success(request, 'Image saved successfully!')
                return JsonResponse({'success': True}) if is_ajax else redirect('home')
            else:
                # Form validation failed
                logger.error(f"Form validation failed: {form.errors}")
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'Invalid form data'})
                messages.error(request, 'Error saving image. Please try again.')
                return redirect('home')

        # Handle AJAX image data
        elif is_ajax:
            effect = request.POST.get('effect_applied', '')
            image_data = request.POST.get('image')

            if not image_data:
                return JsonResponse({'success': False, 'error': 'No image data provided'})

            # Check image format and extract data
            if ';base64,' not in image_data:
                return JsonResponse({'success': False, 'error': 'Invalid image data format'})

            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            img_data = base64.b64decode(imgstr)

            # Create unique identifier for this image
            timestamp = int(time.time())
            unique_id = f"{request.user.id}_{timestamp}"

            # Create and save ImageEdit object
            image_edit = ImageEdit(
                user=request.user,
                effect_applied=effect
            )

            # Save both original and edited versions
            image_edit.original_image.save(f"original_{unique_id}.{ext}", ContentFile(img_data))
            image_edit.edited_image.save(f"edited_{unique_id}_{effect}.{ext}", ContentFile(img_data))
            image_edit.save()

            logger.info(f"AJAX image saved with ID: {image_edit.id}")

            return JsonResponse({
                'success': True,
                'message': 'Image saved successfully',
                'image_id': image_edit.id
            })

    except Exception as e:
        logger.error(f"Error saving image: {str(e)}")
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f'Error saving image: {str(e)}')

    return redirect('home')

@login_required
def delete_image(request, image_id):
    """Delete an image from the user's gallery"""
    # Check if this is an AJAX request - I put this here so it's easy to find
    is_ajax = request.method == 'DELETE' and request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    try:
        # Get and delete the image
        image = get_object_or_404(ImageEdit, id=image_id, user=request.user)
        image.delete()

        # Handle AJAX success response
        if is_ajax:
            return JsonResponse({'success': True})

        # Handle regular form success
        messages.success(request, 'Image deleted successfully!')
    except Exception as e:
        # Handle errors appropriately for request type
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f'Error deleting image: {str(e)}')

    return redirect('home')

@login_required
def share_image(request, image_id):
    """Get a shareable link for the specified image"""
    image = get_object_or_404(ImageEdit, id=image_id, user=request.user)

    # Get full URL to the image
    share_url = request.build_absolute_uri(image.edited_image.url)

    # Return JSON for AJAX requests, otherwise redirect
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'url': share_url})
    return redirect(image.edited_image.url)

def api_overview(request):
    """API documentation endpoint - lists available API endpoints"""
    api_urls = {
        'Apply Effect': '/apply-effect/',
        'Save Image': '/save/',
        'Delete Image': '/delete/<image_id>/',
        'Share Image': '/share/<image_id>/',
    }
    return JsonResponse(api_urls)
