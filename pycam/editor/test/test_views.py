import os
import base64
import json
from io import BytesIO
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages.storage.fallback import FallbackStorage
from PIL import Image as PILImage

from editor.models import ImageEdit
from editor.views import (
    login, homepage, apply_image_effect, save_image,
    delete_image, share_image, api_overview
)


class EditorViewsTestCase(TestCase):
    """Test suite for the editor views."""

    def setUp(self):
        """Set up test environment."""
        # Create test user
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )

        # Set up client and factory
        self.client = Client()
        self.factory = RequestFactory()

        # Create a test image
        self.create_test_image()

        # Create test image in database
        self.image_edit = ImageEdit.objects.create(
            user=self.user,
            original_image=self.test_image_file,
            edited_image=self.test_image_file,
            effect_applied='grayscale'
        )

    def create_test_image(self):
        """Create a test image for testing."""
        # Create a small test image
        img = PILImage.new('RGB', (100, 100), color='red')
        self.img_buffer = BytesIO()
        img.save(self.img_buffer, format='PNG')
        self.img_buffer.seek(0)

        # Create file for upload testing
        self.test_image_file = SimpleUploadedFile(
            'test_image.png',
            self.img_buffer.read(),
            content_type='image/png'
        )
        self.img_buffer.seek(0)

        # Create base64 image for AJAX testing
        img_base64 = base64.b64encode(self.img_buffer.read()).decode('utf-8')
        self.base64_image = f'data:image/png;base64,{img_base64}'

    def add_message_middleware(self, request):
        """Add message middleware to request."""
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request

    def test_login_view(self):
        """Test the login view."""
        # Test redirect for authenticated user
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('login_page'))
        self.assertRedirects(response, reverse('home'))

        # Test login page for unauthenticated user
        self.client.logout()
        response = self.client.get(reverse('login_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_homepage_view(self):
        """Test the homepage view."""
        # Test redirect for unauthenticated user
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('login_page'))

        # Test homepage for authenticated user
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

        # Check that images are in context
        self.assertIn('images', response.context)
        self.assertIn('form', response.context)
        self.assertEqual(len(response.context['images']), 1)

    @patch('editor.views.apply_effect')
    def test_apply_image_effect_valid(self, mock_apply_effect):
        """Test applying an effect with valid data."""
        # Create a mock processed image
        processed_img = PILImage.new('RGB', (100, 100), color='blue')
        mock_buffer = BytesIO()
        processed_img.save(mock_buffer, format='PNG')
        mock_buffer.seek(0)

        # Set up the mock return value
        mock_apply_effect.return_value = processed_img

        # Log in the user
        self.client.login(username=self.username, password=self.password)

        # Set up the request data
        data = {
            'effect': 'grayscale',
            'image': self.base64_image,
            'intensity': 50
        }

        # Make the request
        response = self.client.post(
            reverse('apply_effect'),
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Verify the response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['effect'], 'grayscale')
        self.assertIn('data:image/png;base64,', response_data['image'])

        # Verify the mock was called
        mock_apply_effect.assert_called_once()

    def test_apply_image_effect_missing_data(self):
        """Test applying an effect with missing data."""
        # Log in the user
        self.client.login(username=self.username, password=self.password)

        # Test missing effect
        data = {'image': self.base64_image}
        response = self.client.post(
            reverse('apply_effect'),
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')

        # Test missing image
        data = {'effect': 'grayscale'}
        response = self.client.post(
            reverse('apply_effect'),
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')

    @patch('editor.views.apply_effect')
    def test_save_image_form_upload(self, mock_apply_effect):
        """Test saving an image via form upload."""
        # Create a mock processed image
        processed_img = PILImage.new('RGB', (100, 100), color='blue')
        mock_apply_effect.return_value = processed_img

        # Log in the user
        self.client.login(username=self.username, password=self.password)

        # Set up the data
        self.img_buffer.seek(0)
        test_file = SimpleUploadedFile(
            'new_test.png',
            self.img_buffer.read(),
            content_type='image/png'
        )

        data = {
            'original_image': test_file,
            'effect_applied': 'sepia'
        }

        # Get image count before
        image_count_before = ImageEdit.objects.count()

        # Make the request
        response = self.client.post(reverse('save_image'), data=data)

        # Verify redirect
        self.assertRedirects(response, reverse('home'))

        # Verify new image was created
        self.assertEqual(ImageEdit.objects.count(), image_count_before + 1)
        new_image = ImageEdit.objects.latest('created_at')
        self.assertEqual(new_image.effect_applied, 'sepia')
        self.assertEqual(new_image.user, self.user)

    @patch('editor.views.time.time')
    def test_save_image_ajax(self, mock_time):
        """Test saving an image via AJAX."""
        # Mock the time function to return a consistent value
        mock_time.return_value = 12345

        # Log in the user
        self.client.login(username=self.username, password=self.password)

        # Set up the data
        data = {
            'effect_applied': 'blur',
            'image': self.base64_image
        }

        # Get image count before
        image_count_before = ImageEdit.objects.count()

        # Make the request
        response = self.client.post(
            reverse('save_image'),
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        # Verify new image was created
        self.assertEqual(ImageEdit.objects.count(), image_count_before + 1)
        new_image = ImageEdit.objects.latest('created_at')
        self.assertEqual(new_image.effect_applied, 'blur')
        self.assertEqual(new_image.user, self.user)

    def test_delete_image(self):
        """Test deleting an image."""
        # Log in the user
        self.client.login(username=self.username, password=self.password)

        # Make sure the image exists
        image_id = self.image_edit.id
        self.assertTrue(ImageEdit.objects.filter(id=image_id).exists())

        # Delete the image
        response = self.client.post(reverse('delete_image', args=[image_id]))

        # Verify redirect
        self.assertRedirects(response, reverse('home'))

        # Verify image was deleted
        self.assertFalse(ImageEdit.objects.filter(id=image_id).exists())

    def test_delete_image_ajax(self):
        """Test deleting an image via AJAX."""
        # Log in the user
        self.client.login(username=self.username, password=self.password)

        # Make sure the image exists
        image_id = self.image_edit.id
        self.assertTrue(ImageEdit.objects.filter(id=image_id).exists())

        # Delete the image
        response = self.client.delete(
            reverse('delete_image', args=[image_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])

        # Verify image was deleted
        self.assertFalse(ImageEdit.objects.filter(id=image_id).exists())

    def test_share_image(self):
        """Test sharing an image."""
        # Log in the user
        self.client.login(username=self.username, password=self.password)

        # Get the share url
        response = self.client.get(
            reverse('share_image', args=[self.image_edit.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn(self.image_edit.edited_image.url, response_data['url'])

    def test_api_overview(self):
        """Test the API overview endpoint."""
        response = self.client.get(reverse('api_overview'))

        # Verify response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)

        # Check that the key endpoints are included
        self.assertIn('Apply Effect', response_data)
        self.assertIn('Save Image', response_data)
        self.assertIn('Delete Image', response_data)
        self.assertIn('Share Image', response_data)
