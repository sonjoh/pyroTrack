from django.contrib import admin
from .models import Torrent, Peer

@admin.register(Torrent)
class TorrentAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_by', 'size', 'seeders', 'leechers', 'completed', 'status')
    search_fields = ('name', 'info_hash')
    list_filter = ('status', 'category')


admin.site.register(Peer)
