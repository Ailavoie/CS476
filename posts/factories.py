from .models import DailyPost, MoodPost
from accounts.models import ClientProfile

class PostFactory:
    @staticmethod
    def create_post(post_type: str, client: ClientProfile, data: dict):
        """
        Factory method to create a DailyPost or MoodPost based on post_type.
        Returns the created model instance (DailyPost or MoodPost).
        """
        if post_type == 'daily':
            post = DailyPost.objects.create(
                client=client,
                text=data.get('text', ''),
                commentary=data.get('commentary', '')
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
