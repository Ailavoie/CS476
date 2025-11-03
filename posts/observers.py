from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from django.core.mail import send_mail

# Import new models
from .models import DailyPost, MoodPost
from accounts.models import ClientProfile

class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass


class ConcreteSubject(Subject):
    def __init__(self, model_instance: DailyPost | MoodPost):
        self.model = model_instance
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        print("Subject: Attached an observer.")
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        print("Subject: Notifying observers...")
        for observer in self._observers:
            observer.update(self)

    def set_model(self, value: DailyPost | MoodPost) -> None:
        self.model = value


class Observer(ABC):
    @abstractmethod
    def update(self, subject: Subject) -> None:
        pass


class EmailNotifier(Observer):
    def update(self, subject: Subject) -> None:
        post = subject.model
        client = post.client
        created_at = post.created_at
        client_name = f"{client.first_name} {client.last_name}"
        therapist = getattr(client, "therapist", None)

        if therapist is None:
            print(f"No therapist email found for client {client_name}. Email not sent.")
            return

        therapist_name = f"{therapist.first_name} {therapist.last_name}"
        therapist_email = therapist.user.email
        send_mail(
            subject="New Client Mindlink journal created",
            message=f"Dear {therapist_name}, your client {client_name} created a new post on {created_at.strftime('%Y-%m-%d %H:%M')}. Log into Mindlink to view it.",
            from_email="noreply@example.com",
            recipient_list=[therapist_email],
            fail_silently=False,
        )
        print(f"Email sent to {therapist_email} about new post creation.")


class TherapistNewCommentNotification(Observer):
    def update(self, subject: Subject) -> None:
        post = subject.model
        post.therapist_comment_notification = True
        print(f"TherapistNotification: Reacted to the event. Notification flag set to {post.therapist_comment_notification}")
        post.save()
