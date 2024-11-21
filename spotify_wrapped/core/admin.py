from django.contrib import admin
from .models import SpotifyWrap

@admin.register(SpotifyWrap)
class SpotifyWrapAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')  # Customize columns to show

