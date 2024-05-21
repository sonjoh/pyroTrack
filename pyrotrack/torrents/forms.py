from django import forms

# Class for the form to upload a torrent
class TorrentForm(forms.Form):
    torrent = forms.FileField(label='Select a torrent file')