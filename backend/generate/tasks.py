from celery import shared_task
from .models import Picture
from PIL import Image
import io
import torch
from diffusers import StableDiffusionImg2ImgPipeline

@shared_task
def enhance_picture(picture_id):
    """
    Enhance a picture using Stable Diffusion image-to-image model on GPU only.

    :param picture_id: ID of the picture to enhance
    :return: None
    """
    try:
        # Check GPU availability and force stop if not available
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA GPU is required but not available.")
        
        # Set default tensor type to GPU
        torch.set_default_tensor_type('torch.cuda.FloatTensor')

        # Retrieve the picture from database
        picture = Picture.objects.get(id=picture_id)
        
        # Open the uploaded picture
        uploaded_picture = Image.open(picture.uploaded_picture)
        
        # Ensure image is in RGB mode
        if uploaded_picture.mode == 'RGBA':
            uploaded_picture = uploaded_picture.convert('RGB')
        
        # Resize image to a suitable size for the model
        uploaded_picture = uploaded_picture.resize((768, 512))
        
        # Load the Stable Diffusion model
        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            model_id, 
            torch_dtype=torch.float16
        )
        
        # Optimize for GPU
        pipe = pipe.to("cuda")
        pipe.enable_attention_slicing()
        pipe.enable_xformers_memory_efficient_attention()
        
        # Define enhancement prompt
        enhancement_prompt = (
            "High quality, sharp details, professional photography, "
            "enhanced clarity, vibrant colors, clean and crisp image"
        )
        
        # Perform image enhancement
        enhanced_images = pipe(
            prompt=enhancement_prompt,
            image=uploaded_picture,
            strength=0.75,  # Adjust strength of enhancement
            guidance_scale=7.5
        ).images
        
        # Take the first enhanced image
        enhanced_image = enhanced_images[0]
        
        # Save the enhanced image
        buffer = io.BytesIO()
        enhanced_image.save(buffer, format='JPEG')
        buffer.seek(0)
        picture.enhanced_picture.save(f"enhanced_{picture_id}.jpg", buffer)
        picture.save()
        
        return True
    
    except Exception as e:
        # Log the error
        print(f"Error enhancing picture {picture_id}: {str(e)}")
        return False
