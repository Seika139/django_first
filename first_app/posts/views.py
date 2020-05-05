from django.shortcuts import render ,get_object_or_404
from .models import Post
# from django.http import HttpResponse


def index(request):
    # return HttpResponse("Hello World")

    # postsのデータをpublished_atの順でソートして取得する '-'をつけると逆順
    posts = Post.objects.order_by('-published_at')
    # テンプレートに posts という変数として postsの内容を与える
    return render(request, 'posts/index.html', {'posts': posts })

def detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts/detail.html', {'post': post})
