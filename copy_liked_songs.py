#!/usr/bin/env python3
import os
import sys
from datetime import datetime

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

load_dotenv()

REDIRECT_URI = "http://127.0.0.1:8080"
SCOPE = "user-library-read playlist-modify-public playlist-modify-private"


def get_spotify_client():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Error: Spotify credentials not found!")
        print("Create a .env file with:")
        print("  SPOTIFY_CLIENT_ID=your_client_id")
        print("  SPOTIFY_CLIENT_SECRET=your_client_secret")
        print("\nGet credentials at: https://developer.spotify.com/dashboard")
        sys.exit(1)
    
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            open_browser=True
        ),
        requests_timeout=30
    )


def fetch_all_liked_songs(sp):
    print("Fetching your liked songs...")
    
    liked_tracks = []
    offset = 0
    limit = 50
    
    while True:
        try:
            results = sp.current_user_saved_tracks(limit=limit, offset=offset)
            items = results.get("items", [])
            
            if not items:
                break
            
            for item in items:
                track = item.get("track")
                if track and track.get("id"):
                    liked_tracks.append({
                        "id": track["id"],
                        "name": track["name"],
                        "artists": ", ".join(a["name"] for a in track.get("artists", []))
                    })
            
            offset += limit
            print(f"  Fetched {len(liked_tracks)} songs...", end="\r")
            
        except Exception as e:
            print(f"\nError: {e}")
            sys.exit(1)
    
    print(f"\nTotal: {len(liked_tracks)} songs")
    
    liked_tracks.reverse()
    
    return liked_tracks


def create_playlist(sp, name, description=""):
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=name, public=False, description=description)
    return playlist["id"], playlist["external_urls"]["spotify"]


def add_tracks_to_playlist(sp, playlist_id, track_ids):
    total = len(track_ids)
    batch_size = 100
    
    for i in range(0, total, batch_size):
        batch = track_ids[i:i + batch_size]
        sp.playlist_add_items(playlist_id, batch)
        print(f"  Added {min(i + batch_size, total)}/{total} songs...", end="\r")
    
    print()


def get_existing_playlist_tracks(sp, playlist_id):
    existing_ids = set()
    offset = 0
    limit = 100
    
    while True:
        results = sp.playlist_items(playlist_id, offset=offset, limit=limit, fields="items.track.id")
        items = results.get("items", [])
        
        if not items:
            break
        
        for item in items:
            track = item.get("track")
            if track and track.get("id"):
                existing_ids.add(track["id"])
        
        offset += limit
    
    return existing_ids


def main():
    print("=" * 50)
    print("  Liked Songs to Playlist")
    print("=" * 50)
    print()
    
    sp = get_spotify_client()
    user = sp.current_user()
    print(f"Logged in as: {user['display_name']}")
    print()
    
    liked_songs = fetch_all_liked_songs(sp)
    
    if not liked_songs:
        print("No liked songs found.")
        return
    
    print()
    print("Options:")
    print("  1. Create a new playlist")
    print("  2. Add to an existing playlist")
    print()
    
    choice = input("Choose (1/2) [1]: ").strip() or "1"
    
    if choice == "1":
        default_name = f"Liked Songs - {datetime.now().strftime('%Y-%m-%d')}"
        playlist_name = input(f"Playlist name [{default_name}]: ").strip() or default_name
        
        print(f"\nCreating playlist '{playlist_name}'...")
        playlist_id, playlist_url = create_playlist(sp, playlist_name, "Liked songs backup")
        print(f"Created: {playlist_url}")
        
        track_ids = [t["id"] for t in liked_songs]
        print(f"\nAdding {len(track_ids)} songs...")
        add_tracks_to_playlist(sp, playlist_id, track_ids)
        
    elif choice == "2":
        playlist_url = input("Paste playlist URL: ").strip()
        
        try:
            playlist_id = playlist_url.split("/playlist/")[1].split("?")[0]
        except IndexError:
            print("Invalid URL!")
            return
        
        print("\nChecking for duplicates...")
        existing_ids = get_existing_playlist_tracks(sp, playlist_id)
        print(f"Found {len(existing_ids)} existing tracks")
        
        new_tracks = [t for t in liked_songs if t["id"] not in existing_ids]
        
        if not new_tracks:
            print("All songs already in playlist!")
            return
        
        print(f"\nAdding {len(new_tracks)} new songs...")
        track_ids = [t["id"] for t in new_tracks]
        add_tracks_to_playlist(sp, playlist_id, track_ids)
    
    else:
        print("Invalid option!")
        return
    
    print()
    print("=" * 50)
    print("  Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
