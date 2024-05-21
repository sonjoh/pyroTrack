import bencodepy
import hashlib
import json


def create_info_hash(bencoded_data):
    bencoded_info = bencodepy.encode(bencoded_data['info'])
    infohash = hashlib.sha1(bencoded_info).hexdigest()
    return infohash


def decode_bencode(bencoded_data):
    try:
        decoded_data = bencodepy.decode(bencoded_data)
    except bencodepy.BencodeDecodeError as e:
        print(f"Decoding error: {e}")
        return None

    def convert_bytes(data):
        if isinstance(data, dict):
            return {convert_bytes(key): convert_bytes(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [convert_bytes(item) for item in data]
        elif isinstance(data, bytes):
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                return data  # Return the original bytes if they can't be decoded
        else:
            return data

    return convert_bytes(decoded_data)


def is_valid_bencode(data):
    if not isinstance(data, (bytes, bytearray)):
        return False

    try:
        bencodepy.decode(data)
        return True
    except (bencodepy.BencodeDecodeError, ValueError):
        return False
