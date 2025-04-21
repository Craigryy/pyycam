from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import ImageEdit
from .forms import ImageEditForm
from .effects import apply_effect
import base64
import io
import json
from PIL import Image
import logging
import time

def login(request):
    """
    Custom login view that renders the login.html template.
    """
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'login.html')

@login_required
def homepage(request):
    """
    Main view for the photo editor homepage.
    Displays the editor interface and the user's gallery of edited images.
    """
    if not request.user.is_authenticated:
        # Try multiple approaches to direct to login.html
        return redirect('login_page')

    # Get all images uploaded by the current user
    images = ImageEdit.objects.filter(user=request.user).order_by('-created_at')
    form = ImageEditForm()

    return render(request, 'homepage.html', {
        'images': images,
        'form': form,
    })


def login_view(request):
    """
    Custom login view that renders the login.html template.
    """
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'login.html')


@login_required
@require_POST
def apply_image_effect(request):
    """
    API endpoint to apply an effect to an image and return the result.
    This is called via AJAX from the frontend.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Process AJAX request
            effect_name = request.POST.get('effect')
            image_data = request.POST.get('image')
            intensity = request.POST.get('intensity', 50)

            if not effect_name or not image_data:
                return JsonResponse({'status': 'error', 'message': 'Missing effect or image data'})

            # Process the base64 image
            try:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]

                # Convert base64 to PIL Image
                img_data = base64.b64decode(imgstr)
                img = Image.open(io.BytesIO(img_data))

                # Debug info
                logger = logging.getLogger(__name__)
                logger.info(f"Processing image with effect: {effect_name}")
                logger.info(f"Image size: {img.size}, mode: {img.mode}")

                # Apply the selected effect and ensure it returns a valid image
                processed_image = apply_effect(img, effect_name)

                # Ensure the image is in RGB mode for consistent results
                if processed_image.mode != 'RGB':
                    processed_image = processed_image.convert('RGB')

                # Convert processed image back to base64 for preview
                buffer = io.BytesIO()
                processed_image.save(buffer, format=ext.upper())
                img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

                return JsonResponse({
                    'status': 'success',
                    'image': f'data:image/{ext};base64,{img_str}',
                    'effect': effect_name
                })
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Error processing image: {str(e)}")
                return JsonResponse({'status': 'error', 'message': f'Error processing image: {str(e)}'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
@require_POST
def save_image(request):
    """
    Save an edited image to the user's gallery.
    This is called when the user clicks the Save button.
    """
    try:
        # Set up logging
        logger = logging.getLogger(__name__)
        logger.info(f"Save image request received: {request.headers.get('X-Requested-With')}")

        # Check for file upload first (from form submission)
        if 'original_image' in request.FILES:
            form = ImageEditForm(request.POST, request.FILES)
            if form.is_valid():
                # Create a new ImageEdit object
                image_edit = form.save(commit=False)
                image_edit.user = request.user

                # Get the effect applied
                effect_applied = request.POST.get('effect_applied', '')
                image_edit.effect_applied = effect_applied
                logger.info(f"File upload with effect: {effect_applied}")

                # Process the image with the effect server-side
                if effect_applied and effect_applied != 'original':
                    # Open the uploaded image
                    original_img = Image.open(request.FILES['original_image'])

                    # Apply the effect
                    processed_img = apply_effect(original_img, effect_applied)

                    # Save the processed image
                    buffer = io.BytesIO()
                    img_format = 'JPEG' if request.FILES['original_image'].name.lower().endswith('.jpg') else 'PNG'
                    processed_img.save(buffer, format=img_format)

                    # Save the original image first
                    image_edit.save()

                    # Then save the edited image
                    image_edit.edited_image.save(
                        f"edited_{request.user.id}_{effect_applied}_{int(time.time())}.{img_format.lower()}",
                        ContentFile(buffer.getvalue())
                    )
                else:
                    # No effect - just use original image
                    image_edit.edited_image = image_edit.original_image
                    image_edit.save()

                messages.success(request, 'Image saved successfully!')

                # Redirect or return JSON response
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                return redirect('home')
            else:
                # Form validation failed
                logger.error(f"Form validation failed: {form.errors}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Invalid form data'})
                messages.error(request, 'Error saving image. Please try again.')
                return redirect('home')

        # Handle AJAX requests with image data (from JavaScript)
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            effect = request.POST.get('effect_applied', '')
            image_data = request.POST.get('image')

            logger.info(f"AJAX image save request with effect: {effect}")

            if not image_data:
                logger.error("No image data provided in AJAX request")
                return JsonResponse({'success': False, 'error': 'No image data provided'})

            try:
                # Process the base64 image (already filtered in frontend)
                if ';base64,' not in image_data:
                    logger.error("Invalid image data format")
                    return JsonResponse({'success': False, 'error': 'Invalid image data format'})

                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                img_data = base64.b64decode(imgstr)

                # Generate a unique ID for the image
                timestamp = int(time.time())
                unique_id = f"{request.user.id}_{timestamp}"
                logger.info(f"Generated unique ID for image: {unique_id}")

                # Create an ImageEdit object
                image_edit = ImageEdit(
                    user=request.user,
                    effect_applied=effect
                )

                # Save the original image data (as is)
                original_filename = f"original_{unique_id}.{ext}"
                image_edit.original_image.save(
                    original_filename,
                    ContentFile(img_data)
                )

                # Save the filtered image exactly as received (no reprocessing)
                edited_filename = f"edited_{unique_id}_{effect}.{ext}"
                image_edit.edited_image.save(
                    edited_filename,
                    ContentFile(img_data)
                )

                image_edit.save()
                logger.info(f"Image saved successfully with ID: {image_edit.id}")

                return JsonResponse({
                    'success': True,
                    'message': 'Image saved successfully',
                    'image_id': image_edit.id
                })

            except Exception as e:
                logger.error(f"Error processing AJAX image save: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)})

    except Exception as e:
        logger.error(f"General error in save_image: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f'Error saving image: {str(e)}')

    return redirect('home')


@login_required
def delete_image(request, image_id):
    """
    Delete an image from the user's gallery.
    """
    try:
        image = get_object_or_404(ImageEdit, id=image_id, user=request.user)
        image.delete()

        # For AJAX requests
        if request.method == 'DELETE' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        messages.success(request, 'Image deleted successfully!')
    except Exception as e:
        if request.method == 'DELETE' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, f'Error deleting image: {str(e)}')

    return redirect('home')


@login_required
def share_image(request, image_id):
    """
    Get shareable link for an image.
    """
    image = get_object_or_404(ImageEdit, id=image_id, user=request.user)

    # Create a shareable URL (this is a simple implementation)
    share_url = request.build_absolute_uri(image.edited_image.url)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'url': share_url})

    # For direct browser access, redirect to the image
    return redirect(image.edited_image.url)


def api_overview(request):
    """
    API overview endpoint.
    Provides information about available API endpoints.
    """
    api_urls = {
        'Apply Effect': '/apply-effect/',
        'Save Image': '/save/',
        'Delete Image': '/delete/<image_id>/',
        'Share Image': '/share/<image_id>/',
    }
    return JsonResponse(api_urls)
