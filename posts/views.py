from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View

from collections import defaultdict
from django.db.models.functions import TruncDate 

from accounts.models import ClientProfile
from .models import DailyPost, MoodPost
from .factories import PostFactory
from .observers import ConcreteSubject, EmailNotifier, TherapistNewCommentNotification

# ------------------- CREATE VIEW -------------------
class PostCreateView(LoginRequiredMixin, View):
    template_name = "posts/create_post.html"
    success_url = reverse_lazy("posts:list_posts")

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

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


from collections import defaultdict
from django.urls import reverse_lazy
from django.utils.timezone import localtime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import DailyPost, MoodPost

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

            post_dict = {
                'id': post.pk,
                'time': local_created.strftime('%I:%M %p'),
                'raw_date': date_id,
                'commentary': getattr(post, 'commentary', ''),
                'edit_url': reverse_lazy(
                    'posts:edit_post',
                    kwargs={'post_type': post.post_type + 'post', 'pk': post.pk}
                ),
                'delete_url': reverse_lazy(
                    'posts:delete_post',
                    kwargs={'post_type': post.post_type + 'post', 'pk': post.pk}
                ),
            }

            if post.post_type == 'daily':
                post_dict['text_summary'] = getattr(post, 'text', '')[:150] + '...' if getattr(post, 'text', '') else ''
                post_dict['full_text'] = getattr(post, 'text', '')

            elif post.post_type == 'mood':
                emoji = self.EMOJI_MAP.get(post.mood_emoji, "❓")  # default to question mark if unknown
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
        return render(request, self.template_name, {
            "post": post,
            "post_type": post_type,
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

    def get_queryset(self):
        client_id = self.kwargs["client_id"]
        therapist = self.request.user.therapist_profile
        daily_posts = DailyPost.objects.filter(client__id=client_id, client__therapist=therapist)
        mood_posts = MoodPost.objects.filter(client__id=client_id, client__therapist=therapist)
        all_posts = list(daily_posts) + list(mood_posts)
        return sorted(all_posts, key=lambda x: x.created_at, reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.kwargs["client_id"]
        context["client"] = get_object_or_404(ClientProfile, id=client_id)
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
        model = DailyPost if post_type == "dailypost" else MoodPost
        post = get_object_or_404(model, id=post_id)
        post.therapist_comment_notification = False
        post.save()
        return redirect("posts:list_posts")