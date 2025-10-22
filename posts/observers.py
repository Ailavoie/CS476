from __future__ import annotations
from abc import ABC, abstractmethod
from random import randrange
from typing import List
from .models import Post
from django.core.mail import send_mail


class Subject(ABC):
        
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to the subject.
        """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from the subject.
        """
        pass

    @abstractmethod
    def notify(self) -> None:
        """
        Notify all observers about an event.
        """
        pass


    

# Concrete Subject
# Concrete subjects send notifications to observers when their state changes.
class ConcreteSubject(Subject):
        
        def __init__(self, model_instance):
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


class Observer(ABC):
    @abstractmethod
    def update(self, subject: Subject) -> None:
        """
        Receive update from subject.
        """
        pass
    
class EmailNotifier(Observer):
    def update(self, subject: Subject) -> None:
                print(f"sending post email:")
                
                post = subject.model
                client = subject.model.instance.client
                created_at = subject.model.instance.created_at
                send_mail(
                    subject="New Post Created",
                    message=f"Dear {client.user.email}, your post created at {created_at} has been successfully created.",
                    from_email='noreply@example.com',
                    recipient_list=[client.user.email],
                    fail_silently=False,
                )
                print(f"Email sent to {client.user.email} about new post creation.")
                    