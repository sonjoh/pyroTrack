from django.db import models
from django.contrib.auth import get_user_model

class Torrent(models.Model):
    info_hash = models.CharField(max_length=40, unique=True, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    size = models.BigIntegerField(null=False, blank=False)
    seeders = models.IntegerField(default=0)
    leechers = models.IntegerField(default=0)
    completed = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    file_list = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('deleted', 'Deleted')], default='active')
    private = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_date']

class Peer(models.Model):
    torrent = models.ForeignKey(Torrent, on_delete=models.CASCADE)
    peer_id = models.CharField(max_length=20, unique=True)
    ip = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    uploaded = models.BigIntegerField(default=0)
    downloaded = models.BigIntegerField(default=0)
    left = models.BigIntegerField(default=0)
    event = models.CharField(max_length=10, choices=[('started', 'started'), ('stopped', 'stopped'), ('completed', 'completed')])
    last_announce = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ip}:{self.port} ({self.peer_id})"
