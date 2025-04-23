from django import forms
from .models import ImageEdit

class ImageEditForm(forms.ModelForm):
    """Form for uploading and editing images"""

    # Image upload field with proper attributes for file selection
    original_image = forms.ImageField(
        label='Upload Image',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'image-upload'
        })
    )

    # Hidden field to store which effect was applied
    effect_applied = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'effect-applied'})
    )

    class Meta:
        model = ImageEdit
        fields = ['original_image', 'effect_applied']

    def clean_original_image(self):
        """Validate image file type and size"""
        image = self.cleaned_data.get('original_image')

        if image:
            # Make sure it's actually an image file
            if not image.content_type.startswith('image'):
                raise forms.ValidationError("The uploaded file is not an image.")

            # Limit file size to 5MB to prevent server overload
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large (maximum size is 5MB).")

        return image
