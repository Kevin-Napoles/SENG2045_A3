from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .forms import ProfileForm
from .models import Profile


def my_profile_view(request):
    obj = get_object_or_404(Profile, user_id=request.user.pk)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=obj)

    if request.method == 'POST' and request.is_ajax():
        if form.is_valid():
            instance = form.save()
            return JsonResponse({
                'bio': instance.bio,
                'avatar': instance.avatar.url,
                'user': instance.user.username,
            })
        return JsonResponse({'errors': form.errors.get_json_data()}, status=400)

    context = {'obj': obj, 'form': form}
    return render(request, 'profiles/main.html', context)
