from __future__ import annotations
from abc import ABC, abstractmethod
from random import randrange
from typing import List
from .models import Post
from accounts.models import ClientProfile
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.contrib.sessions.models import Session

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
                client_name = f"{client.first_name} {client.last_name}"
                therapist_name = f"{client.therapist.first_name} {client.therapist.last_name}"
                therapist_email = client.therapist.user.email 

                if therapist_email is None:
                    print(f"No therapist email found for client {client_name}. Email not sent.")
                    return
                else:
                    send_mail(
                        subject="New Client Mindlink journal created",
                        message=f"Dear {therapist_name}, your client {client_name} created a new post. Log into Mindlink to view your client's journal entry",
                        from_email='noreply@example.com',
                        recipient_list=[therapist_email],
                        fail_silently=False,
                    )
                    print(f"Email sent to {therapist_email} about new post creation.")
                    

class PostNotification(Observer):
    def update(self, subject: Subject) -> None:
        print("PostNotification: Reacted to the event.")
    