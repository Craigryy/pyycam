from django import forms
from .models import ImageEdit

class ImageEditForm(forms.ModelForm):
    """
    Form for creating and editing image edits.
    """
    # Add a field for uploaded images
    original_image = forms.ImageField(
        label='Upload Image',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'image-upload'
        })
    )

    # Hidden field for storing the applied effect
    effect_applied = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'effect-applied'})
    )

    class Meta:
        model = ImageEdit
        fields = ['original_image', 'effect_applied']

    def clean_original_image(self):
        """
        Validate that the uploaded file is a valid image.
        """
        image = self.cleaned_data.get('original_image')

        # Check if file is an image
        if image:
            if not image.content_type.startswith('image'):
                raise forms.ValidationError("The uploaded file is not an image.")

            # Check file size (limit to 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large (maximum size is 5MB).")

        return image
