def post(request, pk):
    """Single post with comments and a comment form."""
    post = Post.objects.get(pk=pk)
    comments = Comment.objects.filter(post=post)
    return render(request, "post.html", post=post, comments=comments, form=CommentForm())

def add_comment(request, pk):
    """Add a new comment."""
    user = request.user
    post = request.POST
    body = post.get("body", None)
    if body:
        author  = post.get("author", "Anonymous")
        comment = Comment(post=Post.objects.get(pk=pk), author=author, body=body)
        notify  = True if (user.is_authenticated() and user.is_staff) else False
        comment.save(notify=notify)
    return redir("post", pk=pk)

def archive_month(request, year, month):
    """Monthly archive. (UNUSED)"""
    posts = Post.objects.filter(created__year=year, created__month=month)
    return render(request, "list.html", post_list=posts, months=mkmonth_lst(), archive=True)

def main(request):
    """Main listing (UNUSED)."""
    posts = Post.objects.all().order_by("-created")
    posts = make_paginator(request, posts, per_page=10)
    return render(request, "list.html", posts=posts, post_list=posts.object_list, months=mkmonth_lst())

