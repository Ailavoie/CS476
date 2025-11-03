from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views import View
from collections import defaultdict
from django.db.models.functions import TruncDate 
from accounts.models import ClientProfile
from .models import DailyPost, MoodPost
from .factories import PostFactory
from .observers import ConcreteSubject, EmailNotifier, TherapistNewCommentNotification
from django.utils.timezone import localtime
from .forms import DailyPostForm, MoodPostForm

## ------------------- CREATE VIEW -------------------
class PostCreateView(LoginRequiredMixin, View):
    template_name = "posts/create_post.html"
    success_url = reverse_lazy("posts:list_posts")

    def get(self, request, *args, **kwargs):
        # Instantiates the form needed to load CKEditor assets via {{ form.media }}
        form = DailyPostForm() 
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        post_type = request.POST.get("post_type")
        factory = PostFactory()
        
        post = factory.create_post(post_type, request.user.client_profile, request.POST)
        
        # Notify observers
        concrete_subject = ConcreteSubject(post)
        concrete_observer = EmailNotifier()
        concrete_subject.attach(concrete_observer)
        concrete_subject.notify()

        return redirect(self.success_url)

# ------------------- LIST VIEW -------------------
class PostListView(LoginRequiredMixin, ListView):
    template_name = "posts/list_posts.html"
    context_object_name = "posts"

    EMOJI_MAP = {
        "happy": "😊",
        "neutral": "😐",
        "sad": "😞",
    }

    def get_queryset(self):
        daily_posts = DailyPost.objects.filter(client=self.request.user.client_profile)
        mood_posts = MoodPost.objects.filter(client=self.request.user.client_profile)
        all_posts = list(daily_posts) + list(mood_posts)
        # Sort descending by created_at
        return sorted(all_posts, key=lambda x: x.created_at, reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_posts = context['posts']

        posts_by_date = defaultdict(list)
        for post in all_posts:
            # Convert created_at to local time
            local_created = localtime(post.created_at)
            display_date = local_created.strftime('%B %d, %Y')
            date_id = local_created.strftime('%Y-%m-%d')

            # Determine post type for URL construction
            post_type_url = post.post_type + 'post' 

            post_dict = {
                'id': post.pk,
                'time': local_created.strftime('%I:%M %p'),
                'raw_date': date_id,
                'commentary': getattr(post, 'commentary', ''),
                'edit_url': reverse_lazy('posts:edit_post', kwargs={'post_type': post_type_url, 'pk': post.pk}),
                'delete_url': reverse_lazy('posts:delete_post', kwargs={'post_type': post_type_url, 'pk': post.pk}),
            }

            if post.post_type == 'daily':
                post_dict['text_summary'] = getattr(post, 'text', '')[:150] + '...' if getattr(post, 'text', '') and len(getattr(post, 'text', '')) > 150 else getattr(post, 'text', '')
                post_dict['full_text'] = getattr(post, 'text', '')

            elif post.post_type == 'mood':
                emoji = self.EMOJI_MAP.get(post.mood_emoji, "❓")
                post_dict['text_summary'] = (
                    f"Mood: {emoji}  |  Energy: {post.energy_level}  |  "
                    f"Workout: {'Yes' if post.worked_out else 'No'}  |  "
                    f"Trigger: {post.mood_trigger[:100]}{'...' if len(post.mood_trigger) > 100 else ''}"
                )
                post_dict['full_text'] = (
                    f"Mood: {emoji}\n"
                    f"Energy Level: {post.energy_level}\n"
                    f"Worked Out: {'Yes' if post.worked_out else 'No'}\n"
                    f"Mood Trigger: {post.mood_trigger}"
                )

            posts_by_date[display_date].append(post_dict)

        context['grouped_posts'] = list(posts_by_date.items())
        return context

# ------------------- UPDATE VIEW -------------------
class PostUpdateView(LoginRequiredMixin, View):
    template_name = "posts/edit_post.html"
    success_url = reverse_lazy("posts:list_posts")

    def get_object(self):
        post_type = self.kwargs.get("post_type")
        pk = self.kwargs.get("pk")
        model = DailyPost if post_type == "dailypost" else MoodPost
        return get_object_or_404(model, pk=pk, client=self.request.user.client_profile)

    def get(self, request, pk, post_type):
        post = self.get_object()
        
        # Determine and Instantiate the Form
        if post_type == 'dailypost':
            FormClass = DailyPostForm
        elif post_type == 'moodpost':
            FormClass = MoodPostForm
        else:
            return redirect(self.success_url) 
            
        # Instantiate the correct form class, pre-populated with the instance data
        form = FormClass(instance=post)

        return render(request, self.template_name, {
            "post": post,
            "post_type": post_type,
            "form": form,
        })

    def post(self, request, pk, post_type):
        post = self.get_object()
        factory = PostFactory()
        factory.update_post(post, request.POST)
        return redirect(self.success_url)


# ------------------- DELETE VIEW -------------------
class PostDeleteView(LoginRequiredMixin, View):
    success_url = reverse_lazy("posts:list_posts")

    def get_object(self):
        post_type = self.kwargs.get("post_type")
        pk = self.kwargs.get("pk")
        model = DailyPost if post_type == "dailypost" else MoodPost
        return get_object_or_404(model, pk=pk, client=self.request.user.client_profile)

    def post(self, request, pk, post_type):
        post = self.get_object()
        post.delete()
        return redirect(self.success_url)


# ------------------- THERAPIST VIEWS -------------------
class TherapistClientListView(LoginRequiredMixin, ListView):
    model = ClientProfile
    template_name = "posts/therapist_client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        if hasattr(self.request.user, "therapist_profile"):
            return ClientProfile.objects.filter(therapist=self.request.user.therapist_profile)
        return ClientProfile.objects.none()


class TherapistClientPostsView(LoginRequiredMixin, ListView):
    template_name = "posts/therapist_client_posts.html"
    context_object_name = "posts"
    
    # Define the Emoji Mapping for use in the context data
    EMOJI_MAP = {
        "happy": "😊",
        "neutral": "😐",
        "sad": "😞",
    }

    def get_queryset(self):
        client_id = self.kwargs["client_id"]
        # Ensure the therapist is correct (good security practice)
        therapist = self.request.user.therapist_profile
        
        daily_posts = DailyPost.objects.filter(client__id=client_id, client__therapist=therapist)
        mood_posts = MoodPost.objects.filter(client__id=client_id, client__therapist=therapist)
        
        all_posts = list(daily_posts) + list(mood_posts)
        return sorted(all_posts, key=lambda x: x.created_at, reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.kwargs["client_id"]
        context["client"] = get_object_or_404(ClientProfile, id=client_id)
        
        # --- CRITICAL ADDITION: Prepare posts for template ---
        
        processed_posts = []
        for post in context['posts']:
            # 1. Attach the simple post_type string ('daily' or 'mood')
            #    (Using post.post_type is the preferred approach if available, but isinstance is reliable)
            post_type_slug = 'daily' if isinstance(post, DailyPost) else 'mood'
            post.post_type = post_type_slug
            
            # 2. Attach the emoji for Mood Posts
            if post_type_slug == 'mood':
                # Use getattr safely in case mood_emoji is missing (though it shouldn't be)
                mood_value = getattr(post, 'mood_emoji', None)
                post.emoji = self.EMOJI_MAP.get(mood_value, "❓")
            else:
                # Set a placeholder for Daily posts
                post.emoji = None
            
            processed_posts.append(post)

        # Replace the original queryset results with the decorated list
        context['posts'] = processed_posts
        
        # ---------------------------------------------------
        
        return context

# ------------------- COMMENTS -------------------
class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, post_id, post_type):
        model = DailyPost if post_type == "dailypost" else MoodPost
        post = get_object_or_404(model, id=post_id)

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


# ------------------- CLEAR NOTIFICATIONS -------------------
class ClearNotificationsView(LoginRequiredMixin, View):
    def post(self, request, post_id, post_type):
        model = DailyPost if post_type == "daily" else MoodPost
        post = get_object_or_404(model, id=post_id)
        post.therapist_comment_notification = False
        post.save()
        return redirect("posts:list_posts")