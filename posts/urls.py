from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path("", views.PostListView.as_view(), name="list_posts"),
    #path("list/", views.PostListView.as_view(), name="list_posts"),
    path("create/", views.PostCreateView.as_view(), name="create_post"),
    path("<str:post_type>/<int:pk>/edit/", views.PostUpdateView.as_view(), name="edit_post"),
    path("<str:post_type>/<int:pk>/delete/", views.PostDeleteView.as_view(), name="delete_post"),
    path("therapist/clients/", views.TherapistClientListView.as_view(), name="therapist_clients"),
    path("therapist/clients/<int:client_id>/posts/", views.TherapistClientPostsView.as_view(), name="therapist_client_posts"),
    path('posts/<int:post_id>/<str:post_type>/add_comment/', views.AddCommentView.as_view(), name='add_comment'),
    #path("clear_notifications/<int:post_id>/", views.ClearNotificationsView.as_view(), name="clear_notifications"),
    path("clear_notifications/<int:post_id>/<str:post_type>/", views.ClearNotificationsView.as_view(), name="clear_notifications"),
]