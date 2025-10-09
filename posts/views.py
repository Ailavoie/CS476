from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Post
from .forms import PostForm

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/create_post.html"
    success_url = reverse_lazy("posts:list_posts")

    def form_valid(self, form):
        form.instance.client = self.request.user.client_profile
        return super().form_valid(form)

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/list_posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.filter(client=self.request.user.client_profile).order_by("-created_at")

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/edit_post.html"
    success_url = reverse_lazy("posts:list_posts")

    def get_queryset(self):
        return Post.objects.filter(client=self.request.user.client_profile)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "posts/delete_post.html"
    success_url = reverse_lazy("posts:list_posts")

    def get_queryset(self):
        return Post.objects.filter(client=self.request.user.client_profile)
