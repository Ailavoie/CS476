from .models import DailyPost, MoodPost
from accounts.models import ClientProfile

class PostFactory:
    @staticmethod
    def create_post(post_type: str, client: ClientProfile, data: dict):
        if post_type == 'daily':
            post = DailyPost.objects.create(
                client=client,
                text=data.get('text', ''),
            )
        elif post_type == 'mood':
            post = MoodPost.objects.create(
                client=client,
                mood_emoji=data.get('mood_emoji', ''),
                energy_level=data.get('energy_level', 1),
                mood_trigger=data.get('mood_trigger', ''),
                worked_out=data.get('worked_out', False)
            )
        else:
            raise ValueError(f"Invalid post type: {post_type}")
        return post

    @staticmethod
    def update_post(post, data: dict):
        """
        Update an existing DailyPost or MoodPost instance.
        """
        if isinstance(post, DailyPost):
            post.text = data.get('text', post.text)

        elif isinstance(post, MoodPost):
            post.mood_emoji = data.get('mood_emoji', post.mood_emoji)
            post.energy_level = data.get('energy_level', post.energy_level)
            post.mood_trigger = data.get('mood_trigger', post.mood_trigger)
            worked_out_value = data.get('worked_out')
            if isinstance(worked_out_value, str):
                post.worked_out = worked_out_value.lower() in ['true', '1', 'yes']
            else:
                post.worked_out = bool(worked_out_value)

        post.save()
        return post