# liked-songs-to-playlist

Copy your Spotify liked songs into a regular playlist in the exact same chronological order.

## what's this for?

"Liked Songs" on Spotify is weird - it's not a real playlist, you can't share it, and you can't back it up. This script fixes that by copying all your liked songs into an actual playlist.
This script keeps the songs in **chronological order** - oldest liked song first, newest last.

## how to use

### 1. get spotify api access

create a Spotify app:

1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create App"
   - Name: whatever
   - Description: whatever
   - **Redirect URI**: `http://127.0.0.1:8080` (copy this exactly)
   - Select "Web API"
4. Save it, then click Settings
5. Copy your **Client ID** and **Client Secret**

### 2. install stuff

```bash
pip install -r requirements.txt
```

### 3. add your credentials

Copy `.env.example` to `.env` and fill in your credentials.

### 4. run it

```bash
python copy_liked_songs.py
```

First time it'll open your browser to log in to Spotify. After that it'll
- Grab all your liked songs
- Ask if you want a new playlist or add to an existing one
- Copy everything over in order

## features

- ✅ Works with any number of songs (handles pagination)
- ✅ Keeps chronological order (oldest → newest)
- ✅ Skips duplicates when adding to existing playlists
- ✅ Creates private playlists by default
- ✅ Cross-platform

## faq

**"Redirect URI mismatch" error?**  
Make sure you use `http://127.0.0.1:8080` (not localhost)

**Takes forever with lots of songs?**  
Spotify's API has rate limits.

**Can I run this multiple times?**  
Yes, if you add to an existing playlist, it'll skip songs already there.