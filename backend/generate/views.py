from django.shortcuts import render, redirect
from .forms import PictureForm
from .models import Picture
from .tasks import enhance_picture

def upload_picture(request):
    if request.method == 'POST':
        form = PictureForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.save()
            enhance_picture.delay(picture.id)
            return redirect('generate:result', picture_id=picture.id)
    else:
        form = PictureForm()
    return render(request, 'generate/upload.html', {'form': form})

def result(request, picture_id):
    picture = Picture.objects.get(id=picture_id)
    return render(request, 'generate/result.html', {'picture': picture})