from django.db import models
from django.contrib.auth.models import User

# pretty simple model. user is foreign key, so it accesses data from django default user model
#deletes on cascade, which means if wrap is deleted, then all wraps of that user are deleted

#primary key is also defined as "ID" by
class SpotifyWrap(models.Model):
    """
    Model to store Spotify wrap data associated with a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spotify_wraps')
    title = models.CharField(max_length=255)  # Optional: A title for the wrap
    data = models.JSONField()  # To store the wrap data (in JSON format)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the wrap is created

    def __str__(self):
        return f"{self.title} by {self.user.username}"

class Artist(models.Model):
    name = models.CharField(max_length=255)

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    duration = models.IntegerField()  # Duration in seconds

class UserListeningData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    play_count = models.IntegerField(default=0)

class Invite(models.Model):
    sender = models.ForeignKey(User, related_name="send_invites", on_delete=models.CASCADE)
    recipient_email = models.EmailField()
    invite_code = models.CharField(max_length=255, unique=True)
    is_Accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)