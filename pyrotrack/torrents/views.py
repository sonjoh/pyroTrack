from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from .models import Torrent, Peer
from .forms import TorrentForm
from django.utils import timezone
from datetime import timedelta
from .utils import create_info_hash, decode_bencode, is_valid_bencode
import logging
import urllib.parse
import binascii
import re


logger = logging.getLogger('pyrotrack')


@require_GET
def announce(request):
    query_string = request.META['QUERY_STRING']
    info_hash_pattern = re.compile(r'info_hash=([^&]+)')
    match = info_hash_pattern.search(query_string)
    if match:
        # Extract the URL-encoded info_hash value
        encoded_info_hash = match.group(1)
        info_hash_bytes = urllib.parse.unquote_to_bytes(encoded_info_hash)
        # Convert the bytes to a hexadecimal string
        info_hash = binascii.hexlify(info_hash_bytes).decode('ascii')

    peer_id = request.GET.get('peer_id')
    ip = request.GET.get('ip') or request.META.get('REMOTE_ADDR')
    port = int(request.GET.get('port'))
    uploaded = int(request.GET.get('uploaded', 0))
    downloaded = int(request.GET.get('downloaded', 0))
    left = int(request.GET.get('left', 0))
    event = request.GET.get('event', 'started')
    num_want = int(request.GET.get('numwant', 50))


    logger.info(f"Announce request received: info_hash={info_hash}, peer_id={peer_id}, ip={ip}, port={port}, uploaded={uploaded}, downloaded={downloaded}, left={left}, event={event}, num_want={num_want}")

    #info_hash = urllib.parse.unquote(bytes(info_hash))
    #logger.info(f"info_hash: {info_hash}")

    if not info_hash or not peer_id or not ip or not port:
        return HttpResponse("Invalid request", status=400)
    
    logger.info(f"info_hash: {info_hash}")
    
    try:
        torrent = Torrent.objects.get(info_hash=info_hash)
    except Torrent.DoesNotExist:
        return HttpResponse("Torrent not found", status=404)

    if event == 'stopped':
        Peer.objects.filter(peer_id=peer_id).delete()
        torrent.seeders = Peer.objects.filter(torrent=torrent, left=0).count()
        torrent.leechers = Peer.objects.filter(torrent=torrent, left__gt=0).count()
        torrent.completed = Peer.objects.filter(torrent=torrent, event='completed').count()
        torrent.save()
        return JsonResponse({"peers": []})

    peer, created = Peer.objects.update_or_create(
        peer_id=peer_id,
        defaults={
            'torrent': torrent,
            'ip': ip,
            'port': port,
            'uploaded': uploaded,
            'downloaded': downloaded,
            'left': left,
            'event': event,
            'last_announce': timezone.now()
        }
    )

    # Clean up old peers
    Peer.objects.filter(last_announce__lt=timezone.now() - timedelta(minutes=30)).delete()

    # Find peers to return
    peers = Peer.objects.filter(torrent=torrent).exclude(peer_id=peer_id)[:num_want]
    peer_list = [{'ip': p.ip, 'port': p.port} for p in peers]

    # Update the peer counts for the torrent
    torrent.seeders = Peer.objects.filter(torrent=torrent, left=0).count()
    torrent.leechers = Peer.objects.filter(torrent=torrent, left__gt=0).count()
    torrent.completed = Peer.objects.filter(torrent=torrent, event='completed').count()
    torrent.save()

    response_data = {
        "interval": 1800,  # 30 minutes
        "peers": peer_list
    }

    return JsonResponse(response_data)

@require_GET
def scrape(request):
    query_string = request.META['QUERY_STRING']
    info_hash_pattern = re.compile(r'info_hash=([^&]+)')
    match = info_hash_pattern.search(query_string)
    if match:
        # Extract the URL-encoded info_hash value
        encoded_info_hash = match.group(1)
        info_hash_bytes = urllib.parse.unquote_to_bytes(encoded_info_hash)
        # Convert the bytes to a hexadecimal string
        info_hash = binascii.hexlify(info_hash_bytes).decode('ascii')
        
    if not info_hash:
        return HttpResponse("Invalid request", status=400)

    try:
        torrent = Torrent.objects.get(info_hash=info_hash)
    except Torrent.DoesNotExist:
        return HttpResponse("Torrent not found", status=404)

    response_data = {
        "files": {
            info_hash: {
                "complete": torrent.seeders,
                "downloaded": torrent.completed,
                "incomplete": torrent.leechers
            }
        }
    }

    return JsonResponse(response_data)


def upload_torrent(request):
    # for GET requests, return the form with file upload
    if request.method == 'GET':
        form = TorrentForm()
        return render(request, 'upload_torrent.html', {'form': form})
    
    # for POST requests, process the form data
    if request.method == 'POST':
        form = TorrentForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = request.FILES['torrent']
            file_content = uploaded_file.read()
            data = decode_bencode(file_content)
            if not data:
                return HttpResponse("Invalid torrent file", status=400)

            try:
                if data['info']['private'] and data['info']['private'] != 1:
                    return HttpResponse("Only private torrents are allowed", status=400)
            except KeyError:
                return HttpResponse("Private flag not found in torrent", status=400)

            
            #info_hash = data['info']['hash']
            #info_hash = create_info_hash(data)
            info_hash = create_info_hash(data)

            try:
                torrent = Torrent.objects.get(info_hash=info_hash)
                return HttpResponse("Torrent already exists", status=409)
            except Torrent.DoesNotExist:
                pass
            
            try:
                torrent_size = data['info']['length']
            except KeyError:
                torrent_size = sum(f['length'] for f in data['info']['files'])

            torrent = Torrent(
                info_hash=info_hash,
                name=data['info']['name'],
                size=torrent_size,
                uploaded_by=request.user,
                file_list=data.get('files'),
                status='active',
                private=1
            )

            torrent.save()

            return HttpResponse(f"Torrent uploaded: {torrent.name} ({torrent_size} bytes) with info hash {info_hash}")
    
    return HttpResponse("Invalid request", status=400)