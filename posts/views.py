from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View

from collections import defaultdict
from django.db.models.functions import TruncDate 


from accounts.models import ClientProfile
from .models import Post
from .forms import PostForm
from .observers import Subject, Observer, ConcreteSubject, EmailNotifier, TherapistNewCommentNotification
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
import threading

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/create_post.html"
    success_url = reverse_lazy("posts:list_posts")
    

    print(f"In post create view")
    def form_valid(self, form):
        form.instance.client = self.request.user.client_profile
        print(f"In post create view valid")

        concrete_subject = ConcreteSubject(form)
        concrete_observer = EmailNotifier()
        concrete_subject.attach(concrete_observer)
        concrete_subject.notify()
        
        print(f"notfying observers")
        return super().form_valid(form)

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/list_posts.html"
    context_object_name = "posts"

# Override get_queryset to filter posts by logged in user
    def get_queryset(self):
        return Post.objects.filter(client=self.request.user.client_profile).order_by("-created_at")
    
#Update notifications
    def update_notifications(self):
        posts = self.get_queryset()
        for post in posts:
            if post.therapist_comment_notification:
                post.therapist_comment_notification = False
                post.save()
        return redirect('posts/list_posts.html')
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_posts = context['posts'] # The queryset from get_queryset()

        # Group posts by date
        posts_by_date = defaultdict(list)
        
        for post in all_posts:
            # Format the date as 'October 19, 2025' for display
            display_date = post.created_at.strftime('%B %d, %Y')
            # Use the simple date 'YYYY-MM-DD' for JS element IDs and anchors
            date_id = post.created_at.strftime('%Y-%m-%d')
            
            # Prepare data for the dashboard summary view
            posts_by_date[display_date].append({
                'id': post.pk,
                'time': post.created_at.strftime('%I:%M %p'),
                'raw_date': date_id,
                # Show only the first 150 characters for the summary
                'text_summary': post.text[:150] + '...' if len(post.text) > 150 else post.text,
                'full_text': post.text,
                'commentary': post.commentary,
                'edit_url': reverse_lazy('posts:edit_post', kwargs={'pk': post.pk}),
                'delete_url': reverse_lazy('posts:delete_post', kwargs={'pk': post.pk}),
            })
        
        # Convert the defaultdict to a list of tuples for the template (preserving order)
        context['grouped_posts'] = list(posts_by_date.items())
        
        return context

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
            concrete_subject = ConcreteSubject(post)
            concrete_observer = TherapistNewCommentNotification()
            concrete_subject.attach(concrete_observer)
            concrete_subject.notify()
            concrete_subject.detach(concrete_observer)

        return redirect("posts:therapist_client_posts", client_id=post.client.id)

class ClearNotificationsView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        post.therapist_comment_notification = False
        post.save()
        return redirect("posts:list_posts")