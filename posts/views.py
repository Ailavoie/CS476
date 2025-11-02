from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View

from accounts.models import ClientProfile
from .models import Post
from .forms import PostForm
from .observers import Subject, Observer, ConcreteSubject, EmailNotifier, PostNotification
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/create_post.html"
    success_url = reverse_lazy("posts:list_posts")
    

    print(f"In post create view")
    def form_valid(self, form):
        form.instance.client = self.request.user.client_profile
        print(f"In post create view valid")

        # Save the form first
        response = super().form_valid(form)
        
        # Now notify observers with the saved instance
        concrete_subject = ConcreteSubject(form.instance)  # Pass the saved Post instance
        concrete_observer = EmailNotifier()
        concrete_subject.attach(concrete_observer)
        concrete_observer_notification = PostNotification()
        concrete_subject.attach(concrete_observer_notification)
        concrete_subject.notify()
        
        print(f"notifying observers")

        return response

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/list_posts.html"
    context_object_name = "posts"

# Override get_queryset to filter posts by logged in user
    def get_queryset(self):
        return Post.objects.filter(client=self.request.user.client_profile).order_by("-created_at")

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/edit_post.html"
    success_url = reverse_lazy("posts:list_posts")
# Override get_queryset to ensure only the owner's posts can be edited
    def get_queryset(self):
        return Post.objects.filter(client=self.request.user.client_profile)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "posts/delete_post.html"
    success_url = reverse_lazy("posts:list_posts")
# Override get_queryset to ensure only the owner's posts can be deleted
    def get_queryset(self):
        return Post.objects.filter(client=self.request.user.client_profile)

class TherapistClientListView(LoginRequiredMixin, ListView):
    model = ClientProfile
    template_name = "posts/therapist_client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        if hasattr(self.request.user, "therapist_profile"):
            return ClientProfile.objects.filter(therapist=self.request.user.therapist_profile)
        return ClientProfile.objects.none()
    
class TherapistClientPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/therapist_client_posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        client_id = self.kwargs["client_id"]
        therapist = self.request.user.therapist_profile

        return Post.objects.filter(client__id=client_id, client__therapist=therapist).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.kwargs["client_id"]
        context["client"] = get_object_or_404(ClientProfile, id=client_id)
        return context

class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        if hasattr(request.user, "therapist_profile") and post.client.therapist == request.user.therapist_profile:
            commentary = request.POST.get("commentary", "")
            post.commentary = commentary
            post.save()

        return redirect("posts:therapist_client_posts", client_id=post.client.id)