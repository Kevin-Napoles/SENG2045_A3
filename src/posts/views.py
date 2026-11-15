from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.forms import ImageField, IntegerField
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .forms import PostForm
from .models import Photo, Post
from profiles.models import Profile
# Create your views here.

def post_list_and_create(request):
    form = PostForm(request.POST or None)
    # qs = Post.objects.all()
    if request.is_ajax():
        if form.is_valid():
            author = Profile.objects.get(user=request.user)
            instance = form.save(commit=False)
            instance.author = author
            instance.save()
            return JsonResponse({
                'title': instance.title,
                'body': instance.body,
                'author': instance.author.user.username,
                'id': instance.id,
            })

    context = {
        # 'qs': qs,
        'form': form,
    }
    return render(request, 'posts/main.html', context)

def load_post_data_view(request, num_posts):
    if request.is_ajax():
        visible = 3
        upper = num_posts
        lower = upper - visible
        size = Post.objects.all().count()
        qs = Post.objects.all()
        data = []
        for obj in qs:
            item = {
                'id': obj.id,
                'title': obj.title,
                'body': obj.body,
                'liked': True if request.user in obj.liked.all() else False,
                'count': obj.like_count,
                'author': obj.author.user.username
            }
            data.append(item)
        return JsonResponse({'data':data[lower:upper], 'size': size})

def post_detail_data_view(request, pk):
    obj = Post.objects.get(pk=pk)
    data = {
        'id': obj.id,
        'title': obj.title,
        'body': obj.body,
        'author': obj.author.user.username,
        'logged_in': request.user.username,
    }
    return JsonResponse({'data': data})

def like_unlike_post(request):
    if request.is_ajax():
        pk = request.POST.get('pk')
        obj = Post.objects.get(pk=pk)
        if request.user in obj.liked.all():
            liked = False
            obj.liked.remove(request.user)
        else:
            liked = True
            obj.liked.add(request.user)
        return JsonResponse({'liked': liked, 'count': obj.like_count})

def post_detail(request, pk):
    obj = Post.objects.get(pk=pk)
    form = PostForm()
    context = {
        'obj': obj,
        'form': form,
    }
    return render(request, 'posts/detail.html', context)


@require_POST
def update_post(request, pk):
    if not request.is_ajax():
        return JsonResponse({'error': 'Expected an AJAX request.'}, status=400)

    obj = get_object_or_404(Post, pk=pk, author__user_id=request.user.pk)
    form = PostForm(request.POST, instance=obj)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors.get_json_data()}, status=400)

    obj = form.save(commit=False)
    obj.save(update_fields=('title', 'body', 'updated'))
    return JsonResponse({'title': obj.title, 'body': obj.body})


@require_POST
def delete_post(request, pk):
    if not request.is_ajax():
        return JsonResponse({'error': 'Expected an AJAX request.'}, status=400)

    obj = get_object_or_404(Post, pk=pk, author__user_id=request.user.pk)
    obj.delete()
    return JsonResponse({})


@require_POST
def image_upload_view(request):
    try:
        new_post_id = IntegerField(min_value=1, max_value=2**63 - 1).clean(
            request.POST.get('new_post_id')
        )
    except ValidationError as error:
        return HttpResponseBadRequest(error.messages[0], content_type='text/plain')

    post = get_object_or_404(Post, pk=new_post_id, author__user_id=request.user.pk)

    try:
        img = ImageField().clean(request.FILES.get('file'))
    except ValidationError as error:
        return HttpResponseBadRequest(error.messages[0], content_type='text/plain')

    photo = Photo(post=post)
    photo.image.save(img.name, img, save=False)
    try:
        photo.save()
    except DatabaseError:
        photo.image.delete(save=False)
        raise
    return HttpResponse()
