#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import random
import string
import threading
import requests
import socket
import struct
import socks
import re
import base64
import hashlib
import uuid
import datetime
import itertools
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urlencode
from typing import Optional, List, Dict, Any
from colorama import Fore, Back, Style, init

init(autoreset=True)

# ============================================================
#                    COLOR SHORTCUTS
# ============================================================
R = Fore.RED
G = Fore.GREEN
Y = Fore.YELLOW
B = Fore.BLUE
M = Fore.MAGENTA
C = Fore.CYAN
W = Fore.WHITE
RESET = Style.RESET_ALL
BRIGHT = Style.BRIGHT
DIM = Style.DIM

def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""{C}{BRIGHT}
  __  __      _ _   _    _____         _ 
 |  \\/  |_  _| | |_(_)__|_   _|__  ___| |
 | |\\/| | || | |  _| |___|| |/ _ \\/ _ \\ |
 |_|  |_|\\_,_|_|\\__|_|    |_|\\___/\\___/_|
                                         
{RESET}""")
    print(f"{M}{BRIGHT}{'='*50}{RESET}")
    print(f"{Y}{BRIGHT}         Multi-Tool v1.0 | By MultiTool{RESET}")
    print(f"{M}{BRIGHT}{'='*50}{RESET}")
    print()

# ============================================================
#                    UTILITY FUNCTIONS
# ============================================================

def success(msg): print(f"{G}{BRIGHT}[+]{RESET} {msg}")
def error(msg):   print(f"{R}{BRIGHT}[-]{RESET} {msg}")
def info(msg):    print(f"{C}{BRIGHT}[*]{RESET} {msg}")
def warn(msg):    print(f"{Y}{BRIGHT}[!]{RESET} {msg}")
def inp(msg):     return input(f"{M}{BRIGHT}[>]{RESET} {msg}")

def pause():
    input(f"\n{Y}{BRIGHT}[↵] Press Enter to continue...{RESET}")

def save_to_file(filename: str, data: str, mode: str = 'a'):
    with open(filename, mode, encoding='utf-8') as f:
        f.write(data + '\n')
    success(f"Saved to {filename}")

def load_file(filename: str) -> List[str]:
    if not os.path.exists(filename):
        error(f"File not found: {filename}")
        return []
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip() for line in f if line.strip()]

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def separator(char='─', length=50, color=C):
    print(f"{color}{BRIGHT}{char * length}{RESET}")

def header(title: str):
    clear()
    banner()
    separator()
    print(f"{Y}{BRIGHT}  ► {title}{RESET}")
    separator()
    print()

# ============================================================
#              DISCORD API HELPER
# ============================================================

DISCORD_API = "https://discord.com/api/v9"

def discord_headers(token: str) -> Dict:
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Super-Properties": base64.b64encode(json.dumps({
            "os": "Windows", "browser": "Chrome", "device": "",
            "system_locale": "en-US", "browser_version": "108.0.0.0",
            "os_version": "10", "referrer": "", "referring_domain": "",
            "release_channel": "stable", "client_build_number": 160544,
            "client_event_source": None
        }).encode()).decode()
    }

def validate_token(token: str) -> Optional[Dict]:
    try:
        r = requests.get(f"{DISCORD_API}/users/@me",
                         headers=discord_headers(token), timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

# ============================================================
#           1. DISCORD TOKEN VALIDATOR
# ============================================================

def discord_token_validator():
    header("Discord Token Validator")
    choice = inp("(1) Single Token  (2) File: ").strip()

    tokens = []
    if choice == '1':
        t = inp("Enter Token: ").strip()
        tokens = [t]
    else:
        path = inp("File Path: ").strip()
        tokens = load_file(path)

    if not tokens:
        error("No tokens provided.")
        pause(); return

    valid, invalid = [], []
    info(f"Checking {len(tokens)} token(s)...\n")

    def check(token):
        data = validate_token(token)
        if data:
            uid   = data.get('id', 'N/A')
            uname = data.get('username', 'N/A')
            disc  = data.get('discriminator', '0000')
            email = data.get('email', 'N/A')
            phone = data.get('phone', 'N/A')
            mfa   = data.get('mfa_enabled', False)
            nitro = "Nitro" if data.get('premium_type', 0) > 0 else "None"
            print(f"{G}[VALID]{RESET} {uname}#{disc} | ID: {uid} | Email: {email} | Phone: {phone} | MFA: {mfa} | Nitro: {nitro}")
            valid.append(f"{token} | {uname}#{disc} | {uid} | {email} | MFA:{mfa} | {nitro}")
        else:
            print(f"{R}[INVALID]{RESET} {token[:30]}...")
            invalid.append(token)

    with ThreadPoolExecutor(max_workers=10) as ex:
        ex.map(check, tokens)

    print()
    info(f"Valid: {len(valid)} | Invalid: {len(invalid)}")
    if valid:
        save_to_file("valid_tokens.txt", '\n'.join(valid))
    pause()

# ============================================================
#           2. DISCORD TOKEN ONLINER
# ============================================================

def discord_token_onliner():
    header("Discord Token Onliner")
    path = inp("Token file (one per line): ").strip()
    tokens = load_file(path)
    if not tokens:
        pause(); return

    statuses = ["online", "idle", "dnd"]
    status   = inp("Status (online/idle/dnd) [default: online]: ").strip() or "online"
    if status not in statuses:
        status = "online"

    stop_event = threading.Event()

    def keep_online(token):
        ws_url = "wss://gateway.discord.gg/?v=9&encoding=json"
        import websocket
        def on_open(ws):
            payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {"$os": "Windows", "$browser": "Chrome", "$device": ""},
                    "presence": {"status": status, "afk": False}
                }
            }
            ws.send(json.dumps(payload))

        def on_message(ws, message):
            data = json.loads(message)
            if data.get('op') == 10:
                interval = data['d']['heartbeat_interval'] / 1000
                def heartbeat():
                    while not stop_event.is_set():
                        ws.send(json.dumps({"op": 1, "d": None}))
                        time.sleep(interval)
                threading.Thread(target=heartbeat, daemon=True).start()

        def on_error(ws, err): pass
        def on_close(ws, *a): pass

        try:
            ws = websocket.WebSocketApp(ws_url, on_open=on_open,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.run_forever()
        except Exception as e:
            error(f"WS Error: {e}")

    info(f"Onlining {len(tokens)} token(s) with status: {status}")
    warn("Press Ctrl+C to stop.\n")

    threads = []
    for token in tokens:
        t = threading.Thread(target=keep_online, args=(token,), daemon=True)
        t.start()
        threads.append(t)
        success(f"Started onliner for: {token[:30]}...")
        time.sleep(0.3)

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        warn("Stopped all onliners.")
    pause()

# ============================================================
#           3. DISCORD TOKEN INFO
# ============================================================

def discord_token_info():
    header("Discord Token Info")
    token = inp("Enter Token: ").strip()
    data  = validate_token(token)
    if not data:
        error("Invalid token."); pause(); return

    separator()
    fields = {
        "Username":       f"{data.get('username')}#{data.get('discriminator')}",
        "User ID":        data.get('id'),
        "Email":          data.get('email', 'N/A'),
        "Phone":          data.get('phone', 'N/A'),
        "MFA Enabled":    data.get('mfa_enabled'),
        "Verified":       data.get('verified'),
        "Nitro Type":     data.get('premium_type', 0),
        "Locale":         data.get('locale'),
        "Created":        str(datetime.datetime.utcfromtimestamp(
                              ((int(data.get('id', 0)) >> 22) + 1420070400000) / 1000
                          )),
        "Avatar":         f"https://cdn.discordapp.com/avatars/{data.get('id')}/{data.get('avatar')}.png"
                          if data.get('avatar') else "None",
        "Flags":          data.get('flags', 0),
        "Public Flags":   data.get('public_flags', 0),
    }
    for k, v in fields.items():
        print(f"  {C}{BRIGHT}{k:<16}{RESET}: {W}{v}{RESET}")
    separator()

    # Guilds
    try:
        r = requests.get(f"{DISCORD_API}/users/@me/guilds",
                         headers=discord_headers(token), timeout=10)
        if r.status_code == 200:
            guilds = r.json()
            info(f"Member of {len(guilds)} guild(s):")
            for g in guilds[:10]:
                print(f"  {G}•{RESET} {g.get('name')} (ID: {g.get('id')})")
            if len(guilds) > 10:
                warn(f"  ... and {len(guilds)-10} more")
    except Exception: pass

    save_choice = inp("\nSave info? (y/n): ").strip().lower()
    if save_choice == 'y':
        out = json.dumps(data, indent=2)
        save_to_file(f"token_info_{data.get('id')}.json", out, 'w')
    pause()

# ============================================================
#           4. DISCORD TOKEN NUKER
# ============================================================

def discord_token_nuker():
    header("Discord Token Nuker")
    warn("This tool is for educational purposes only!")
    warn("Use only on your own accounts!\n")

    token = inp("Enter Token: ").strip()
    data  = validate_token(token)
    if not data:
        error("Invalid token."); pause(); return

    success(f"Logged in as: {data.get('username')}#{data.get('discriminator')}")

    print(f"\n{Y}Actions:{RESET}")
    print("  [1] Leave All Guilds")
    print("  [2] Delete All DMs")
    print("  [3] Unfriend Everyone")
    print("  [4] Change Username")
    print("  [5] All of the above")
    print("  [0] Back")

    ch = inp("Choice: ").strip()
    hdrs = discord_headers(token)

    def leave_guilds():
        r = requests.get(f"{DISCORD_API}/users/@me/guilds", headers=hdrs, timeout=10)
        if r.status_code == 200:
            for g in r.json():
                gid = g.get('id')
                is_owner = g.get('owner', False)
                if not is_owner:
                    dr = requests.delete(f"{DISCORD_API}/users/@me/guilds/{gid}", headers=hdrs)
                    if dr.status_code in [200, 204]:
                        success(f"Left guild: {g.get('name')}")
                    time.sleep(0.5)

    def delete_dms():
        r = requests.get(f"{DISCORD_API}/users/@me/channels", headers=hdrs, timeout=10)
        if r.status_code == 200:
            for ch_data in r.json():
                cid = ch_data.get('id')
                dr = requests.delete(f"{DISCORD_API}/channels/{cid}", headers=hdrs)
                if dr.status_code in [200, 204]:
                    success(f"Closed DM: {cid}")
                time.sleep(0.3)

    def unfriend_all():
        r = requests.get(f"{DISCORD_API}/users/@me/relationships", headers=hdrs, timeout=10)
        if r.status_code == 200:
            for rel in r.json():
                uid = rel.get('id')
                dr  = requests.delete(f"{DISCORD_API}/users/@me/relationships/{uid}", headers=hdrs)
                if dr.status_code in [200, 204]:
                    success(f"Unfriended: {rel.get('user', {}).get('username')}")
                time.sleep(0.3)

    def change_username():
        new_u = inp("New username: ").strip()
        pwd   = inp("Account password: ").strip()
        r = requests.patch(f"{DISCORD_API}/users/@me", headers=hdrs,
                           json={"username": new_u, "password": pwd})
        if r.status_code == 200:
            success(f"Username changed to: {new_u}")
        else:
            error(f"Failed: {r.text}")

    if   ch == '1': leave_guilds()
    elif ch == '2': delete_dms()
    elif ch == '3': unfriend_all()
    elif ch == '4': change_username()
    elif ch == '5':
        leave_guilds(); delete_dms(); unfriend_all()
    pause()

# ============================================================
#           5. DISCORD TOKEN CLONER (Copy Profile)
# ============================================================

def discord_token_cloner():
    header("Discord Token Cloner")
    src   = inp("Source token: ").strip()
    dst   = inp("Destination token: ").strip()

    src_data = validate_token(src)
    dst_data = validate_token(dst)

    if not src_data:
        error("Source token invalid."); pause(); return
    if not dst_data:
        error("Destination token invalid."); pause(); return

    info(f"Cloning profile from {src_data.get('username')} → {dst_data.get('username')}")

    dst_hdrs = discord_headers(dst)
    password = inp("Destination account password (needed for changes): ").strip()

    payload = {"username": src_data.get('username')}
    if password:
        payload['password'] = password

    # Bio
    try:
        r = requests.get(f"{DISCORD_API}/users/@me/profile",
                         headers=discord_headers(src), timeout=10)
        if r.status_code == 200:
            bio = r.json().get('user_profile', {}).get('bio', '')
            if bio:
                requests.patch(f"{DISCORD_API}/users/@me/profile",
                               headers=dst_hdrs, json={"bio": bio})
                success(f"Cloned bio: {bio[:40]}...")
    except Exception: pass

    # Avatar
    av_hash = src_data.get('avatar')
    if av_hash:
        av_url = f"https://cdn.discordapp.com/avatars/{src_data['id']}/{av_hash}.png?size=1024"
        av_r   = requests.get(av_url)
        if av_r.status_code == 200:
            b64 = base64.b64encode(av_r.content).decode()
            payload['avatar'] = f"data:image/png;base64,{b64}"

    r = requests.patch(f"{DISCORD_API}/users/@me", headers=dst_hdrs, json=payload)
    if r.status_code == 200:
        success("Profile cloned successfully!")
    else:
        error(f"Partial failure: {r.status_code} {r.text[:100]}")
    pause()

# ============================================================
#           6. DISCORD WEBHOOK SPAMMER
# ============================================================

def discord_webhook_spammer():
    header("Discord Webhook Spammer")
    url     = inp("Webhook URL: ").strip()
    message = inp("Message: ").strip()
    amount  = int(inp("Amount (0 = infinite): ").strip() or "10")
    delay   = float(inp("Delay (seconds, default 0.5): ").strip() or "0.5")
    username= inp("Username (optional): ").strip() or None
    avatar  = inp("Avatar URL (optional): ").strip() or None

    payload = {"content": message}
    if username: payload['username'] = username
    if avatar:   payload['avatar_url'] = avatar

    count = 0
    info("Starting spam... Ctrl+C to stop.\n")
    try:
        while amount == 0 or count < amount:
            r = requests.post(url, json=payload, timeout=10)
            if r.status_code in [200, 204]:
                count += 1
                print(f"\r{G}Sent: {count}{RESET}", end='', flush=True)
            elif r.status_code == 429:
                retry = r.json().get('retry_after', 1)
                time.sleep(retry)
                continue
            else:
                warn(f"\nError {r.status_code}: {r.text[:60]}")
            time.sleep(delay)
    except KeyboardInterrupt:
        pass
    print()
    success(f"Total sent: {count}")
    pause()

# ============================================================
#           7. DISCORD WEBHOOK DELETER
# ============================================================

def discord_webhook_deleter():
    header("Discord Webhook Deleter")
    url = inp("Webhook URL: ").strip()
    confirm = inp(f"Delete webhook {url[:50]}...? (y/n): ").strip().lower()
    if confirm != 'y':
        warn("Cancelled."); pause(); return
    r = requests.delete(url, timeout=10)
    if r.status_code == 204:
        success("Webhook deleted!")
    else:
        error(f"Failed: {r.status_code} {r.text}")
    pause()

# ============================================================
#           8. DISCORD WEBHOOK INFO
# ============================================================

def discord_webhook_info():
    header("Discord Webhook Info")
    url = inp("Webhook URL: ").strip()
    r   = requests.get(url, timeout=10)
    if r.status_code != 200:
        error(f"Invalid webhook: {r.status_code}"); pause(); return

    data = r.json()
    separator()
    fields = {
        "Name":        data.get('name'),
        "ID":          data.get('id'),
        "Token":       data.get('token'),
        "Channel ID":  data.get('channel_id'),
        "Guild ID":    data.get('guild_id'),
        "Type":        data.get('type'),
        "Avatar":      f"https://cdn.discordapp.com/avatars/{data.get('id')}/{data.get('avatar')}.png"
                       if data.get('avatar') else "None",
    }
    for k, v in fields.items():
        print(f"  {C}{BRIGHT}{k:<12}{RESET}: {W}{v}{RESET}")
    separator()

    if data.get('source_guild'):
        sg = data['source_guild']
        info(f"Source Guild: {sg.get('name')} ({sg.get('id')})")
    pause()

# ============================================================
#           9. DISCORD WEBHOOK EMBED SENDER
# ============================================================

def discord_webhook_embed():
    header("Discord Webhook Embed Sender")
    url   = inp("Webhook URL: ").strip()

    print(f"\n{Y}Build your embed:{RESET}")
    title       = inp("Title: ").strip()
    description = inp("Description: ").strip()
    color_hex   = inp("Color (hex, e.g. ff0000): ").strip() or "00ff00"
    footer_text = inp("Footer text: ").strip()
    image_url   = inp("Image URL (optional): ").strip()
    thumbnail   = inp("Thumbnail URL (optional): ").strip()
    author_name = inp("Author name (optional): ").strip()
    username    = inp("Webhook username (optional): ").strip() or None
    avatar_url  = inp("Webhook avatar URL (optional): ").strip() or None

    try:
        color_int = int(color_hex.lstrip('#'), 16)
    except Exception:
        color_int = 65280

    embed: Dict[str, Any] = {
        "title": title,
        "description": description,
        "color": color_int,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }
    if footer_text:
        embed["footer"] = {"text": footer_text}
    if image_url:
        embed["image"] = {"url": image_url}
    if thumbnail:
        embed["thumbnail"] = {"url": thumbnail}
    if author_name:
        embed["author"] = {"name": author_name}

    payload: Dict[str, Any] = {"embeds": [embed]}
    if username:   payload['username']   = username
    if avatar_url: payload['avatar_url'] = avatar_url

    r = requests.post(url, json=payload, timeout=10)
    if r.status_code in [200, 204]:
        success("Embed sent!")
    else:
        error(f"Failed: {r.status_code} {r.text}")
    pause()

# ============================================================
#           10. DISCORD SERVER SCRAPER
# ============================================================

def discord_server_scraper():
    header("Discord Server Scraper")
    token   = inp("Token: ").strip()
    guild_id= inp("Guild ID: ").strip()
    hdrs    = discord_headers(token)

    # Guild info
    r = requests.get(f"{DISCORD_API}/guilds/{guild_id}?with_counts=true",
                     headers=hdrs, timeout=10)
    if r.status_code != 200:
        error("Cannot access guild."); pause(); return

    g = r.json()
    separator()
    info("Guild Information:")
    gfields = {
        "Name":          g.get('name'),
        "ID":            g.get('id'),
        "Description":   g.get('description', 'N/A'),
        "Owner ID":      g.get('owner_id'),
        "Members":       g.get('approximate_member_count', 'N/A'),
        "Online":        g.get('approximate_presence_count', 'N/A'),
        "Boost Level":   g.get('premium_tier'),
        "Boosts":        g.get('premium_subscription_count', 0),
        "Verification":  g.get('verification_level'),
        "Region":        g.get('region', 'N/A'),
        "Icon":          f"https://cdn.discordapp.com/icons/{g['id']}/{g['icon']}.png"
                         if g.get('icon') else "None",
        "Banner":        f"https://cdn.discordapp.com/banners/{g['id']}/{g['banner']}.png"
                         if g.get('banner') else "None",
    }
    for k, v in gfields.items():
        print(f"  {C}{BRIGHT}{k:<14}{RESET}: {W}{v}{RESET}")

    # Channels
    rc = requests.get(f"{DISCORD_API}/guilds/{guild_id}/channels", headers=hdrs, timeout=10)
    channels = []
    if rc.status_code == 200:
        channels = rc.json()
        separator()
        info(f"Channels ({len(channels)}):")
        for ch in channels:
            ctype = {0:"Text", 2:"Voice", 4:"Category", 5:"Announcement",
                     13:"Stage", 15:"Forum"}.get(ch.get('type', 0), "Other")
            print(f"  {G}#{ch.get('name')}{RESET} ({ctype}) ID:{ch.get('id')}")

    # Roles
    rr = requests.get(f"{DISCORD_API}/guilds/{guild_id}/roles", headers=hdrs, timeout=10)
    if rr.status_code == 200:
        roles = rr.json()
        separator()
        info(f"Roles ({len(roles)}):")
        for role in roles:
            print(f"  {M}@{role.get('name')}{RESET} (ID:{role.get('id')} | Pos:{role.get('position')})")

    # Emojis
    re2 = requests.get(f"{DISCORD_API}/guilds/{guild_id}/emojis", headers=hdrs, timeout=10)
    if re2.status_code == 200:
        emojis = re2.json()
        separator()
        info(f"Emojis ({len(emojis)}):")
        names = [e.get('name') for e in emojis]
        print("  " + " | ".join(names[:30]) + ("..." if len(names) > 30 else ""))

    save_choice = inp("\nSave scrape? (y/n): ").strip().lower()
    if save_choice == 'y':
        out = {"guild": g, "channels": channels}
        save_to_file(f"scrape_{guild_id}.json", json.dumps(out, indent=2), 'w')
    pause()

# ============================================================
#           11. DISCORD DM SPAMMER
# ============================================================

def discord_dm_spammer():
    header("Discord DM Spammer")
    warn("Educational purposes only!\n")
    token   = inp("Token: ").strip()
    user_id = inp("Target User ID: ").strip()
    message = inp("Message: ").strip()
    amount  = int(inp("Amount (0 = infinite): ").strip() or "5")
    delay   = float(inp("Delay (seconds): ").strip() or "1.0")
    hdrs    = discord_headers(token)

    # Open DM
    r = requests.post(f"{DISCORD_API}/users/@me/channels",
                      headers=hdrs,
                      json={"recipient_id": user_id}, timeout=10)
    if r.status_code != 200:
        error(f"Cannot open DM: {r.status_code}"); pause(); return

    ch_id = r.json().get('id')
    success(f"DM channel opened: {ch_id}")

    count = 0
    try:
        while amount == 0 or count < amount:
            sr = requests.post(f"{DISCORD_API}/channels/{ch_id}/messages",
                               headers=hdrs, json={"content": message}, timeout=10)
            if sr.status_code == 200:
                count += 1
                print(f"\r{G}Sent: {count}{RESET}", end='', flush=True)
            elif sr.status_code == 429:
                retry = sr.json().get('retry_after', 1)
                time.sleep(retry)
                continue
            else:
                warn(f"\nFailed: {sr.status_code}")
            time.sleep(delay)
    except KeyboardInterrupt:
        pass
    print()
    success(f"Sent {count} messages.")
    pause()

# ============================================================
#           12. DISCORD TOKEN JOINER (Join Server)
# ============================================================

def discord_token_joiner():
    header("Discord Token Joiner")
    choice = inp("(1) Single token  (2) File: ").strip()
    tokens = []
    if choice == '1':
        tokens = [inp("Token: ").strip()]
    else:
        tokens = load_file(inp("File path: ").strip())

    invite = inp("Invite code (without discord.gg/): ").strip()
    delay  = float(inp("Delay between joins (seconds): ").strip() or "1.0")

    for token in tokens:
        try:
            r = requests.post(f"{DISCORD_API}/invites/{invite}",
                              headers=discord_headers(token),
                              json={}, timeout=10)
            if r.status_code == 200:
                guild = r.json().get('guild', {}).get('name', 'Unknown')
                success(f"Joined: {guild} | Token: {token[:25]}...")
            elif r.status_code == 429:
                ra = r.json().get('retry_after', 1)
                warn(f"Rate limited. Waiting {ra}s...")
                time.sleep(ra)
                continue
            else:
                error(f"Failed ({r.status_code}): {token[:25]}...")
        except Exception as e:
            error(f"Exception: {e}")
        time.sleep(delay)
    pause()

# ============================================================
#           13. DISCORD TOKEN LEAVER (Leave Server)
# ============================================================

def discord_token_leaver():
    header("Discord Token Leaver")
    token    = inp("Token: ").strip()
    guild_id = inp("Guild ID: ").strip()
    hdrs     = discord_headers(token)
    r = requests.delete(f"{DISCORD_API}/users/@me/guilds/{guild_id}", headers=hdrs, timeout=10)
    if r.status_code in [200, 204]:
        success("Left guild!")
    else:
        error(f"Failed: {r.status_code} {r.text}")
    pause()

# ============================================================
#           14. DISCORD FRIEND ADDER
# ============================================================

def discord_friend_adder():
    header("Discord Friend Adder")
    token    = inp("Token: ").strip()
    username = inp("Username (without discriminator): ").strip()
    discrim  = inp("Discriminator (e.g. 1234): ").strip()
    hdrs     = discord_headers(token)
    payload  = {"username": username, "discriminator": int(discrim)}
    r = requests.post(f"{DISCORD_API}/users/@me/relationships",
                      headers=hdrs, json=payload, timeout=10)
    if r.status_code == 204:
        success(f"Friend request sent to {username}#{discrim}!")
    else:
        error(f"Failed: {r.status_code} {r.text}")
    pause()

# ============================================================
#           15. DISCORD MASS MESSAGE DELETER
# ============================================================

def discord_mass_delete():
    header("Discord Mass Message Deleter")
    token  = inp("Token: ").strip()
    ch_id  = inp("Channel ID: ").strip()
    amount = int(inp("How many messages to delete: ").strip() or "10")
    hdrs   = discord_headers(token)
    me     = validate_token(token)
    if not me:
        error("Invalid token."); pause(); return
    my_id  = me.get('id')

    deleted = 0
    last_id = None
    info(f"Fetching and deleting messages in channel {ch_id}...\n")

    while deleted < amount:
        params = {"limit": 100}
        if last_id:
            params["before"] = last_id
        r = requests.get(f"{DISCORD_API}/channels/{ch_id}/messages",
                         headers=hdrs, params=params, timeout=10)
        if r.status_code != 200:
            error(f"Cannot fetch messages: {r.status_code}"); break

        messages = r.json()
        if not messages:
            break

        for msg in messages:
            if deleted >= amount:
                break
            if msg.get('author', {}).get('id') == my_id:
                dr = requests.delete(f"{DISCORD_API}/channels/{ch_id}/messages/{msg['id']}",
                                     headers=hdrs, timeout=10)
                if dr.status_code == 204:
                    deleted += 1
                    print(f"\r{G}Deleted: {deleted}/{amount}{RESET}", end='', flush=True)
                elif dr.status_code == 429:
                    time.sleep(dr.json().get('retry_after', 1))
                time.sleep(0.3)
            last_id = msg['id']

    print()
    success(f"Deleted {deleted} messages.")
    pause()

# ============================================================
#           16. DISCORD TYPING INDICATOR
# ============================================================

def discord_typing():
    header("Discord Typing Indicator")
    token   = inp("Token: ").strip()
    ch_id   = inp("Channel ID: ").strip()
    duration= int(inp("Duration (seconds): ").strip() or "10")
    hdrs    = discord_headers(token)

    info(f"Sending typing indicator for {duration}s...")
    end = time.time() + duration
    while time.time() < end:
        requests.post(f"{DISCORD_API}/channels/{ch_id}/typing",
                      headers=hdrs, timeout=5)
        time.sleep(8)
    success("Done.")
    pause()

# ============================================================
#           17. DISCORD REACTION ADDER
# ============================================================

def discord_reaction_adder():
    header("Discord Reaction Adder")
    token   = inp("Token: ").strip()
    ch_id   = inp("Channel ID: ").strip()
    msg_id  = inp("Message ID: ").strip()
    emoji   = inp("Emoji (e.g. 👍 or name:id): ").strip()
    hdrs    = discord_headers(token)

    from urllib.parse import quote
    emoji_enc = quote(emoji)
    r = requests.put(
        f"{DISCORD_API}/channels/{ch_id}/messages/{msg_id}/reactions/{emoji_enc}/@me",
        headers=hdrs, timeout=10
    )
    if r.status_code == 204:
        success(f"Reacted with {emoji}!")
    else:
        error(f"Failed: {r.status_code} {r.text}")
    pause()

# ============================================================
#           18. DISCORD GUILD CREATOR
# ============================================================

def discord_guild_creator():
    header("Discord Guild Creator")
    token = inp("Token: ").strip()
    name  = inp("Guild name: ").strip()
    hdrs  = discord_headers(token)
    r = requests.post(f"{DISCORD_API}/guilds",
                      headers=hdrs, json={"name": name}, timeout=10)
    if r.status_code == 201:
        g = r.json()
        success(f"Guild created: {g.get('name')} (ID: {g.get('id')})")
    else:
        error(f"Failed: {r.status_code} {r.text}")
    pause()

# ============================================================
#           19. DISCORD CHANNEL CREATOR
# ============================================================

def discord_channel_creator():
    header("Discord Channel Creator")
    token    = inp("Token: ").strip()
    guild_id = inp("Guild ID: ").strip()
    name     = inp("Channel name: ").strip()
    ctype    = int(inp("Type (0=Text, 2=Voice, 4=Category): ").strip() or "0")
    hdrs     = discord_headers(token)
    r = requests.post(f"{DISCORD_API}/guilds/{guild_id}/channels",
                      headers=hdrs,
                      json={"name": name, "type": ctype}, timeout=10)
    if r.status_code == 201:
        ch = r.json()
        success(f"Channel created: #{ch.get('name')} (ID: {ch.get('id')})")
    else:
        error(f"Failed: {r.status_code} {r.text}")
    pause()

# ============================================================
#           20. DISCORD INVITE CREATOR
# ============================================================

def discord_invite_creator():
    header("Discord Invite Creator")
    token   = inp("Token: ").strip()
    ch_id   = inp("Channel ID: ").strip()
    max_age = int(inp("Max age in seconds (0=infinite): ").strip() or "86400")
    max_use = int(inp("Max uses (0=infinite): ").strip() or "0")
    hdrs    = discord_headers(token)
    r = requests.post(f"{DISCORD_API}/channels/{ch_id}/invites",
                      headers=hdrs,
                      json={"max_age": max_age, "max_uses": max_use}, timeout=10)
    if r.status_code == 200:
        code = r.json().get('code')
        success(f"Invite: https://discord.gg/{code}")
    else:
        error(f"Failed: {r.status_code} {r.text}")
    pause()

# ============================================================
#           21. DISCORD ROLE CREATOR
# ============================================================

def discord_role_creator():
    header("Discord Role Creator")
    token    = inp("Token: ").strip()
    guild_id = inp("Guild ID: ").strip()
    name     = inp("Role name: ").strip()
    color    = inp("Color (hex, e.g. ff0000): ").strip() or "00ff00"
    hdrs     = discord_headers(token)
    try:
        color_int = int(color.lstrip('#'), 16)
    except Exception:
        color_int = 0

    r = requests.post(f"{DISCORD_API}/guilds/{guild_id}/roles",
                      headers=hdrs,
                      json={"name": name, "color": color_int, "hoist": False}, timeout=10)
    if r.status_code == 200:
        role = r.json()
        success(f"Role created: @{role.get('name')} (ID: {role.get('id')})")
    else:
        error(f"Failed: {r.status_code} {r.text}")
    pause()

# ============================================================
#           22. DISCORD NITRO GENERATOR + CHECKER
# ============================================================

def discord_nitro_gen():
    header("Discord Nitro Generator & Checker")
    amount  = int(inp("How many codes to generate: ").strip() or "10")
    check   = inp("Check codes? (y/n): ").strip().lower() == 'y'
    token   = None
    if check:
        token = inp("Token for checking (optional): ").strip() or None

    chars   = string.ascii_letters + string.digits
    valid_c = []

    info(f"Generating {amount} codes...\n")
    for i in range(amount):
        code = ''.join(random.choices(chars, k=16))
        url  = f"https://discord.gift/{code}"

        if check:
            try:
                r = requests.get(f"{DISCORD_API}/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true",
                                 timeout=5)
                if r.status_code == 200:
                    plan = r.json().get('subscription_plan', {}).get('name', 'Unknown')
                    print(f"{G}[VALID]{RESET} {url} | Plan: {plan}")
                    valid_c.append(url)
                else:
                    print(f"{R}[INVALID]{RESET} {url}")
            except Exception:
                print(f"{Y}[ERROR]{RESET} {url}")
            time.sleep(0.2)
        else:
            print(f"{C}{url}{RESET}")

        save_to_file("nitro_codes.txt", url)

    if check:
        info(f"\nValid codes found: {len(valid_c)}")
    pause()

# ============================================================
#           23. PROXY SCRAPER
# ============================================================

PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=socks4",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    "https://openproxy.space/list/http",
    "https://openproxy.space/list/socks4",
    "https://openproxy.space/list/socks5",
]

def proxy_scraper():
    header("Proxy Scraper")
    print("  [1] HTTP   [2] SOCKS4   [3] SOCKS5   [4] All")
    choice = inp("Type: ").strip()

    type_filter = {'1': 'http', '2': 'socks4', '3': 'socks5', '4': 'all'}.get(choice, 'all')
    proxies = set()

    info(f"Scraping proxies ({type_filter})...\n")

    for source in PROXY_SOURCES:
        if type_filter != 'all':
            if type_filter not in source:
                continue
        try:
            r = requests.get(source, timeout=10)
            if r.status_code == 200:
                lines = r.text.strip().split('\n')
                valid_lines = [l.strip() for l in lines if ':' in l.strip()]
                proxies.update(valid_lines)
                info(f"Got {len(valid_lines)} from {source[:50]}")
        except Exception as e:
            error(f"Failed: {source[:40]} - {e}")

    proxies = list(proxies)
    success(f"\nTotal proxies scraped: {len(proxies)}")
    fname = f"proxies_{type_filter}.txt"
    with open(fname, 'w') as f:
        f.write('\n'.join(proxies))
    success(f"Saved to {fname}")
    pause()

# ============================================================
#           24. PROXY CHECKER
# ============================================================

def check_proxy(proxy: str, ptype: str, timeout: int = 5) -> Optional[float]:
    try:
        start = time.time()
        if ptype == 'http':
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
        elif ptype == 'socks4':
            proxies = {"http": f"socks4://{proxy}", "https": f"socks4://{proxy}"}
            r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
        elif ptype == 'socks5':
            proxies = {"http": f"socks5://{proxy}", "https": f"socks5://{proxy}"}
            r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
        else:
            return None
        if r.status_code == 200:
            return round((time.time() - start) * 1000, 2)
    except Exception:
        pass
    return None

def proxy_checker():
    header("Proxy Checker")
    path  = inp("Proxy file (ip:port): ").strip()
    ptype = inp("Type (http/socks4/socks5): ").strip().lower() or "http"
    timeout= int(inp("Timeout (seconds, default 5): ").strip() or "5")
    threads= int(inp("Threads (default 50): ").strip() or "50")

    proxies = load_file(path)
    if not proxies:
        pause(); return

    working = []
    checked = 0
    lock    = threading.Lock()

    def test(proxy):
        nonlocal checked
        ms = check_proxy(proxy, ptype, timeout)
        with lock:
            checked += 1
            if ms:
                working.append(f"{proxy} [{ms}ms]")
                print(f"\r{G}[LIVE]{RESET} {proxy:<22} {ms}ms | Checked: {checked}/{len(proxies)}", end='')
            else:
                print(f"\r{R}[DEAD]{RESET} {proxy:<22} | Checked: {checked}/{len(proxies)}", end='')

    info(f"Checking {len(proxies)} proxies with {threads} threads...\n")

    with ThreadPoolExecutor(max_workers=threads) as ex:
        ex.map(test, proxies)

    print()
    success(f"\nWorking: {len(working)} / {len(proxies)}")
    if working:
        fname = f"working_{ptype}.txt"
        with open(fname, 'w') as f:
            f.write('\n'.join(working))
        success(f"Saved to {fname}")
    pause()

# ============================================================
#           25. PROXY ROTATOR
# ============================================================

proxy_pool   = []
proxy_index  = 0

def proxy_rotator_load():
    header("Proxy Rotator")
    global proxy_pool, proxy_index
    path = inp("Proxy file: ").strip()
    proxy_pool  = load_file(path)
    proxy_index = 0
    if proxy_pool:
        success(f"Loaded {len(proxy_pool)} proxies into rotator!")
    pause()

def get_next_proxy(ptype='http') -> Optional[Dict]:
    global proxy_index
    if not proxy_pool:
        return None
    proxy = proxy_pool[proxy_index % len(proxy_pool)]
    proxy_index += 1
    return {
        "http":  f"{ptype}://{proxy}",
        "https": f"{ptype}://{proxy}"
    }

# ============================================================
#           26. IP LOOKUP
# ============================================================

def ip_lookup():
    header("IP Lookup")
    ip = inp("IP address (leave blank for your IP): ").strip() or ""
    url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query,mobile,proxy,hosting"
    r   = requests.get(url, timeout=10)
    if r.status_code != 200:
        error("API error."); pause(); return

    data = r.json()
    if data.get('status') != 'success':
        error(data.get('message', 'Failed')); pause(); return

    separator()
    fields = {
        "IP":           data.get('query'),
        "Country":      f"{data.get('country')} ({data.get('countryCode')})",
        "Region":       f"{data.get('regionName')} ({data.get('region')})",
        "City":         data.get('city'),
        "ZIP":          data.get('zip'),
        "Latitude":     data.get('lat'),
        "Longitude":    data.get('lon'),
        "Timezone":     data.get('timezone'),
        "ISP":          data.get('isp'),
        "Organization": data.get('org'),
        "AS":           data.get('as'),
        "Mobile":       data.get('mobile'),
        "Proxy/VPN":    data.get('proxy'),
        "Hosting":      data.get('hosting'),
    }
    for k, v in fields.items():
        flag = f"{R}✓{RESET}" if k in ["Proxy/VPN", "Hosting"] and v else ""
        print(f"  {C}{BRIGHT}{k:<14}{RESET}: {W}{v}{RESET} {flag}")
    separator()
    pause()

# ============================================================
#           27. WEBHOOK LOGGER
# ============================================================

def webhook_logger():
    header("Webhook Logger / HTTP Grabber")
    warn("Start a local server to capture incoming webhook data.\n")
    port = int(inp("Port (default 8080): ").strip() or "8080")

    from http.server import HTTPServer, BaseHTTPRequestHandler

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            body   = self.rfile.read(length).decode('utf-8', errors='ignore')
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log = f"[{timestamp}] POST {self.path}\nHeaders: {dict(self.headers)}\nBody: {body}\n{'='*60}"
            print(f"\n{G}[INCOMING REQUEST]{RESET}\n{log}")
            save_to_file("webhook_log.txt", log)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')

        def do_GET(self):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log = f"[{timestamp}] GET {self.path}\nHeaders: {dict(self.headers)}\n{'='*60}"
            print(f"\n{C}[INCOMING GET]{RESET}\n{log}")
            save_to_file("webhook_log.txt", log)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')

        def log_message(self, *args): pass

    server = HTTPServer(('0.0.0.0', port), Handler)
    success(f"Listening on port {port}... Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        warn("Server stopped.")
    pause()

# ============================================================
#           28. DISCORD TOKEN CHANGER
# ============================================================

def discord_token_changer():
    header("Discord Token Changer (Password/Email/Username)")
    token = inp("Token: ").strip()
    hdrs  = discord_headers(token)

    data  = validate_token(token)
    if not data:
        error("Invalid token."); pause(); return

    success(f"Logged in as: {data.get('username')}#{data.get('discriminator')}")

    print(f"\n{Y}What to change?{RESET}")
    print("  [1] Username")
    print("  [2] Email")
    print("  [3] Password")
    print("  [4] Avatar (from URL)")
    ch = inp("Choice: ").strip()

    payload = {}
    password = inp("Current password: ").strip()
    payload['password'] = password

    if ch == '1':
        payload['username'] = inp("New username: ").strip()
    elif ch == '2':
        payload['email'] = inp("New email: ").strip()
    elif ch == '3':
        payload['new_password'] = inp("New password: ").strip()
    elif ch == '4':
        url = inp("Avatar image URL: ").strip()
        r   = requests.get(url)
        if r.status_code == 200:
            b64 = base64.b64encode(r.content).decode()
            ext = url.split('.')[-1].lower()
            if ext not in ['png', 'jpg', 'jpeg', 'gif']:
                ext = 'png'
            payload['avatar'] = f"data:image/{ext};base64,{b64}"

    r = requests.patch(f"{DISCORD_API}/users/@me", headers=hdrs, json=payload, timeout=10)
    if r.status_code == 200:
        success("Account updated successfully!")
        new_data = r.json()
        if 'token' in new_data:
            new_tok = new_data['token']
            success(f"New Token: {new_tok}")
            save_to_file("new_token.txt", new_tok)
    else:
        error(f"Failed: {r.status_code} {r.text[:200]}")
    pause()

# ============================================================
#           29. DISCORD MASS GUILD CHANNEL SPAMMER
# ============================================================

def discord_guild_spammer():
    header("Discord Guild Channel Spammer")
    token    = inp("Token: ").strip()
    guild_id = inp("Guild ID: ").strip()
    message  = inp("Message: ").strip()
    amount   = int(inp("Amount per channel: ").strip() or "5")
    delay    = float(inp("Delay (seconds): ").strip() or "0.5")
    hdrs     = discord_headers(token)

    r = requests.get(f"{DISCORD_API}/guilds/{guild_id}/channels", headers=hdrs, timeout=10)
    if r.status_code != 200:
        error("Cannot fetch channels."); pause(); return

    channels = [c for c in r.json() if c.get('type') == 0]  # Text channels
    info(f"Found {len(channels)} text channels. Spamming...")

    for ch in channels:
        ch_id   = ch.get('id')
        ch_name = ch.get('name')
        count   = 0
        for _ in range(amount):
            sr = requests.post(f"{DISCORD_API}/channels/{ch_id}/messages",
                               headers=hdrs, json={"content": message}, timeout=10)
            if sr.status_code == 200:
                count += 1
                print(f"\r  {G}#{ch_name}{RESET} - Sent: {count}/{amount}", end='', flush=True)
            elif sr.status_code == 429:
                time.sleep(sr.json().get('retry_after', 1))
                continue
            time.sleep(delay)
        print()
    success("Done!")
    pause()

# ============================================================
#           30. DISCORD GUILD NUKER (Admin Token)
# ============================================================

def discord_guild_nuker():
    header("Discord Guild Nuker")
    warn("Educational purposes only! Use on your own servers!\n")
    token    = inp("Admin/Owner Token: ").strip()
    guild_id = inp("Guild ID: ").strip()
    hdrs     = discord_headers(token)

    print(f"\n{R}{BRIGHT}ACTIONS:{RESET}")
    print("  [1] Delete All Channels")
    print("  [2] Delete All Roles")
    print("  [3] Ban Everyone")
    print("  [4] Create Spam Channels")
    print("  [5] All")
    print("  [0] Back")
    ch = inp("Choice: ").strip()

    def delete_channels():
        r = requests.get(f"{DISCORD_API}/guilds/{guild_id}/channels", headers=hdrs, timeout=10)
        if r.status_code == 200:
            for c in r.json():
                dr = requests.delete(f"{DISCORD_API}/channels/{c['id']}", headers=hdrs)
                if dr.status_code == 200:
                    success(f"Deleted channel: #{c.get('name')}")
                time.sleep(0.3)

    def delete_roles():
        r = requests.get(f"{DISCORD_API}/guilds/{guild_id}/roles", headers=hdrs, timeout=10)
        if r.status_code == 200:
            for role in r.json():
                if role.get('name') == '@everyone':
                    continue
                dr = requests.delete(f"{DISCORD_API}/guilds/{guild_id}/roles/{role['id']}", headers=hdrs)
                if dr.status_code == 200:
                    success(f"Deleted role: @{role.get('name')}")
                time.sleep(0.3)

    def ban_everyone():
        r = requests.get(f"{DISCORD_API}/guilds/{guild_id}/members?limit=1000", headers=hdrs, timeout=10)
        if r.status_code == 200:
            for m in r.json():
                uid = m.get('user', {}).get('id')
                br  = requests.put(f"{DISCORD_API}/guilds/{guild_id}/bans/{uid}",
                                   headers=hdrs, json={"delete_message_days": 0})
                if br.status_code == 204:
                    success(f"Banned: {m.get('user', {}).get('username')}")
                time.sleep(0.5)

    def create_spam_channels():
        num = int(inp("How many spam channels: ").strip() or "10")
        name= inp("Channel name: ").strip() or "nuked"
        for i in range(num):
            r = requests.post(f"{DISCORD_API}/guilds/{guild_id}/channels",
                              headers=hdrs,
                              json={"name": f"{name}-{i+1}", "type": 0})
            if r.status_code == 201:
                success(f"Created: #{name}-{i+1}")
            time.sleep(0.3)

    if   ch == '1': delete_channels()
    elif ch == '2': delete_roles()
    elif ch == '3': ban_everyone()
    elif ch == '4': create_spam_channels()
    elif ch == '5':
        delete_channels()
        delete_roles()
        create_spam_channels()
    pause()

# ============================================================
#           31. WEBHOOK MULTI-SENDER
# ============================================================

def webhook_multi_sender():
    header("Webhook Multi-Sender")
    wh_file = inp("Webhook file (one per line): ").strip()
    webhooks= load_file(wh_file)
    if not webhooks:
        pause(); return

    message = inp("Message: ").strip()
    username= inp("Username (optional): ").strip() or None
    avatar  = inp("Avatar URL (optional): ").strip() or None
    delay   = float(inp("Delay (seconds, default 0): ").strip() or "0")

    payload = {"content": message}
    if username: payload['username'] = username
    if avatar:   payload['avatar_url'] = avatar

    success_count = 0
    for wh in webhooks:
        try:
            r = requests.post(wh, json=payload, timeout=10)
            if r.status_code in [200, 204]:
                success_count += 1
                print(f"{G}[SENT]{RESET} {wh[:50]}")
            else:
                print(f"{R}[FAIL]{RESET} {wh[:50]} - {r.status_code}")
        except Exception as e:
            print(f"{R}[ERR]{RESET} {wh[:50]} - {e}")
        time.sleep(delay)

    info(f"\nSent to {success_count}/{len(webhooks)} webhooks.")
    pause()

# ============================================================
#           32. WEBHOOK CHECKER
# ============================================================

def webhook_checker():
    header("Webhook Checker")
    choice = inp("(1) Single  (2) File: ").strip()
    webhooks = []
    if choice == '1':
        webhooks = [inp("Webhook URL: ").strip()]
    else:
        webhooks = load_file(inp("File path: ").strip())

    valid, invalid = [], []
    for wh in webhooks:
        try:
            r = requests.get(wh, timeout=5)
            if r.status_code == 200:
                data = r.json()
                name = data.get('name', 'N/A')
                gid  = data.get('guild_id', 'N/A')
                print(f"{G}[VALID]{RESET} {wh[:60]} | Name: {name} | Guild: {gid}")
                valid.append(wh)
            else:
                print(f"{R}[INVALID]{RESET} {wh[:60]} - {r.status_code}")
                invalid.append(wh)
        except Exception as e:
            print(f"{R}[ERROR]{RESET} {wh[:60]} - {e}")
            invalid.append(wh)

    info(f"\nValid: {len(valid)} | Invalid: {len(invalid)}")
    if valid:
        save_to_file("valid_webhooks.txt", '\n'.join(valid))
    pause()

# ============================================================
#           33. PORT SCANNER
# ============================================================

def port_scanner():
    header("Port Scanner")
    host     = inp("Target host/IP: ").strip()
    port_range= inp("Port range (e.g. 1-1000): ").strip()
    threads  = int(inp("Threads (default 100): ").strip() or "100")

    try:
        start_port, end_port = map(int, port_range.split('-'))
    except Exception:
        error("Invalid range."); pause(); return

    open_ports = []
    lock       = threading.Lock()
    scanned    = 0
    total      = end_port - start_port + 1

    def scan(port):
        nonlocal scanned
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            result = s.connect_ex((host, port))
            s.close()
            with lock:
                scanned += 1
                if result == 0:
                    service = ""
                    try:
                        service = socket.getservbyport(port)
                    except Exception:
                        pass
                    open_ports.append((port, service))
                    print(f"\n{G}[OPEN]{RESET} Port {port} {f'({service})' if service else ''}")
                print(f"\r{C}Scanning... {scanned}/{total}{RESET}", end='', flush=True)
        except Exception:
            pass

    info(f"Scanning {host}:{start_port}-{end_port} with {threads} threads...\n")
    with ThreadPoolExecutor(max_workers=threads) as ex:
        ex.map(scan, range(start_port, end_port + 1))

    print()
    separator()
    success(f"Open ports: {len(open_ports)}")
    for p, s in sorted(open_ports):
        print(f"  {G}{p}{RESET} {f'- {s}' if s else ''}")

    if open_ports:
        out = '\n'.join([f"{p} {s}" for p, s in open_ports])
        save_to_file(f"ports_{host}.txt", out)
    pause()

# ============================================================
#           34. DISCORD TOKEN SPAMMER (Mass Tokens)
# ============================================================

def discord_mass_token_spammer():
    header("Discord Mass Token Message Spammer")
    token_file = inp("Token file: ").strip()
    tokens     = load_file(token_file)
    ch_id      = inp("Channel ID: ").strip()
    message    = inp("Message: ").strip()
    amount     = int(inp("Amount per token: ").strip() or "5")
    delay      = float(inp("Delay (seconds): ").strip() or "0.5")

    if not tokens:
        pause(); return

    def spam_token(token):
        hdrs = discord_headers(token)
        data = validate_token(token)
        if not data:
            error(f"Invalid token: {token[:25]}")
            return
        name = f"{data.get('username')}#{data.get('discriminator')}"
        for _ in range(amount):
            r = requests.post(f"{DISCORD_API}/channels/{ch_id}/messages",
                              headers=hdrs, json={"content": message}, timeout=10)
            if r.status_code == 200:
                print(f"{G}[{name}]{RESET} Message sent!")
            elif r.status_code == 429:
                time.sleep(r.json().get('retry_after', 1))
                continue
            time.sleep(delay)

    with ThreadPoolExecutor(max_workers=len(tokens)) as ex:
        ex.map(spam_token, tokens)
    pause()

# ============================================================
#           35. STRING TOOLS
# ============================================================

def string_tools():
    header("String Tools")
    print("  [1]  Base64 Encode")
    print("  [2]  Base64 Decode")
    print("  [3]  MD5 Hash")
    print("  [4]  SHA1 Hash")
    print("  [5]  SHA256 Hash")
    print("  [6]  SHA512 Hash")
    print("  [7]  URL Encode")
    print("  [8]  URL Decode")
    print("  [9]  Reverse String")
    print("  [10] Random String")
    print("  [11] String to Hex")
    print("  [12] Hex to String")
    print("  [0]  Back")

    ch = inp("Choice: ").strip()
    text = ""
    if ch not in ['10', '0']:
        text = inp("Input: ").strip()

    from urllib.parse import quote, unquote

    result = None
    if   ch == '1':  result = base64.b64encode(text.encode()).decode()
    elif ch == '2':
        try: result = base64.b64decode(text).decode()
        except Exception: result = "Invalid base64"
    elif ch == '3':  result = hashlib.md5(text.encode()).hexdigest()
    elif ch == '4':  result = hashlib.sha1(text.encode()).hexdigest()
    elif ch == '5':  result = hashlib.sha256(text.encode()).hexdigest()
    elif ch == '6':  result = hashlib.sha512(text.encode()).hexdigest()
    elif ch == '7':  result = quote(text)
    elif ch == '8':  result = unquote(text)
    elif ch == '9':  result = text[::-1]
    elif ch == '10':
        length = int(inp("Length: ").strip() or "16")
        chars  = inp("Chars (alphanumeric/letters/digits/custom): ").strip()
        if chars == 'alphanumeric': charset = string.ascii_letters + string.digits
        elif chars == 'letters':    charset = string.ascii_letters
        elif chars == 'digits':     charset = string.digits
        elif chars:                 charset = chars
        else:                       charset = string.ascii_letters + string.digits
        result = ''.join(random.choices(charset, k=length))
    elif ch == '11': result = text.encode().hex()
    elif ch == '12':
        try: result = bytes.fromhex(text).decode()
        except Exception: result = "Invalid hex"
    elif ch == '0': return

    if result is not None:
        print(f"\n{G}Result:{RESET} {result}")
        save = inp("Save result? (y/n): ").strip().lower()
        if save == 'y':
            save_to_file("string_results.txt", result)
    pause()

# ============================================================
#           36. DISCORD GUILD MEMBER SCRAPER
# ============================================================

def discord_member_scraper():
    header("Discord Guild Member Scraper")
    token    = inp("Token: ").strip()
    guild_id = inp("Guild ID: ").strip()
    hdrs     = discord_headers(token)

    members  = []
    last_id  = None
    info("Scraping members (API limit: 1000 per request)...\n")

    while True:
        params = {"limit": 1000}
        if last_id:
            params['after'] = last_id
        r = requests.get(f"{DISCORD_API}/guilds/{guild_id}/members",
                         headers=hdrs, params=params, timeout=10)
        if r.status_code != 200:
            error(f"Error: {r.status_code}"); break

        batch = r.json()
        if not batch:
            break

        for m in batch:
            u     = m.get('user', {})
            line  = f"{u.get('username')}#{u.get('discriminator')} | {u.get('id')} | Bot:{u.get('bot',False)}"
            members.append(line)
            print(f"  {G}•{RESET} {line}")

        last_id = batch[-1].get('user', {}).get('id')
        if len(batch) < 1000:
            break
        time.sleep(0.5)

    success(f"\nScraped {len(members)} members!")
    if members:
        fname = f"members_{guild_id}.txt"
        with open(fname, 'w') as f:
            f.write('\n'.join(members))
        success(f"Saved to {fname}")
    pause()

# ============================================================
#           37. DISCORD BOT TOKEN CHECKER
# ============================================================

def discord_bot_checker():
    header("Discord Bot Token Checker")
    token = inp("Bot token: ").strip()
    # Bot tokens use "Bot " prefix
    if not token.startswith("Bot "):
        token_to_check = f"Bot {token}"
    else:
        token_to_check = token

    try:
        r = requests.get(f"{DISCORD_API}/users/@me",
                         headers={"Authorization": token_to_check}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            success("Valid Bot Token!")
            print(f"  {C}Name:{RESET} {data.get('username')}#{data.get('discriminator')}")
            print(f"  {C}ID:{RESET}   {data.get('id')}")
            print(f"  {C}Bot:{RESET}  {data.get('bot', False)}")
            print(f"  {C}Verified:{RESET} {data.get('verified')}")

            # Get guilds
            rg = requests.get(f"{DISCORD_API}/users/@me/guilds",
                              headers={"Authorization": token_to_check}, timeout=10)
            if rg.status_code == 200:
                guilds = rg.json()
                info(f"In {len(guilds)} guild(s)")
        else:
            error(f"Invalid bot token: {r.status_code}")
    except Exception as e:
        error(f"Error: {e}")
    pause()

# ============================================================
#           38. DISCORD INVITE INFO
# ============================================================

def discord_invite_info():
    header("Discord Invite Info")
    code = inp("Invite code (without discord.gg/): ").strip()
    r    = requests.get(f"{DISCORD_API}/invites/{code}?with_counts=true&with_expiration=true",
                        timeout=10)
    if r.status_code != 200:
        error(f"Invalid invite: {r.status_code}"); pause(); return

    data  = r.json()
    guild = data.get('guild', {})
    ch    = data.get('channel', {})
    inv   = data.get('inviter', {})

    separator()
    info("Guild:")
    print(f"  {C}Name:{RESET}    {guild.get('name')}")
    print(f"  {C}ID:{RESET}      {guild.get('id')}")
    print(f"  {C}Desc:{RESET}    {guild.get('description', 'N/A')}")
    print(f"  {C}Members:{RESET} {data.get('approximate_member_count', 'N/A')}")
    print(f"  {C}Online:{RESET}  {data.get('approximate_presence_count', 'N/A')}")
    print(f"  {C}Verification:{RESET} {guild.get('verification_level')}")
    print(f"  {C}NSFW:{RESET}    {guild.get('nsfw', False)}")
    print(f"  {C}Boost Lvl:{RESET} {guild.get('premium_tier', 0)}")
    print(f"  {C}Icon:{RESET}    https://cdn.discordapp.com/icons/{guild.get('id')}/{guild.get('icon')}.png" if guild.get('icon') else "")

    info("\nChannel:")
    print(f"  {C}Name:{RESET} {ch.get('name')}")
    print(f"  {C}ID:{RESET}   {ch.get('id')}")
    print(f"  {C}Type:{RESET} {ch.get('type')}")

    if inv:
        info("\nInviter:")
        print(f"  {C}Username:{RESET} {inv.get('username')}#{inv.get('discriminator')}")
        print(f"  {C}ID:{RESET}       {inv.get('id')}")

    if data.get('expires_at'):
        print(f"\n{Y}Expires:{RESET} {data.get('expires_at')}")
    separator()
    pause()

# ============================================================
#           39. DISCORD CUSTOM STATUS SETTER
# ============================================================

def discord_custom_status():
    header("Discord Custom Status Setter")
    token  = inp("Token: ").strip()
    emoji  = inp("Emoji (e.g. 🎮, optional): ").strip() or None
    text   = inp("Status text: ").strip()
    status = inp("Status (online/idle/dnd/invisible): ").strip() or "online"
    hdrs   = discord_headers(token)

    import websocket

    custom_status = {"text": text, "emoji_name": emoji} if emoji else {"text": text}

    payload = json.dumps({
        "op": 3,
        "d": {
            "status": status,
            "afk": False,
            "activities": [{
                "type": 4,
                "state": text,
                "name": "Custom Status",
                "emoji": {"name": emoji} if emoji else None
            }],
            "since": 0
        }
    })

    auth_payload = json.dumps({
        "op": 2,
        "d": {
            "token": token,
            "capabilities": 4093,
            "properties": {"os": "Windows", "browser": "Chrome", "device": ""},
            "presence": {
                "status": status,
                "since": 0,
                "activities": [{
                    "type": 4,
                    "state": text,
                    "name": "Custom Status",
                }],
                "afk": False
            }
        }
    })

    sent = threading.Event()

    def on_open(ws):
        ws.send(auth_payload)

    def on_message(ws, message):
        data = json.loads(message)
        if data.get('op') == 10:
            interval = data['d']['heartbeat_interval'] / 1000
            ws.send(json.dumps({"op": 1, "d": None}))
            time.sleep(0.5)
            ws.send(payload)
            time.sleep(1)
            sent.set()
            ws.close()

    def on_error(ws, err): error(str(err))
    def on_close(ws, *a):  pass

    ws = websocket.WebSocketApp(
        "wss://gateway.discord.gg/?v=9&encoding=json",
        on_open=on_open, on_message=on_message,
        on_error=on_error, on_close=on_close
    )

    t = threading.Thread(target=ws.run_forever, daemon=True)
    t.start()
    sent.wait(timeout=15)

    if sent.is_set():
        success(f"Custom status set: {emoji or ''} {text}")
    else:
        error("Failed to set status.")
    pause()

# ============================================================
#           40. DISCORD TOKEN MASS REACTION
# ============================================================

def discord_mass_reaction():
    header("Discord Mass Reaction")
    token_file = inp("Token file: ").strip()
    tokens     = load_file(token_file)
    ch_id      = inp("Channel ID: ").strip()
    msg_id     = inp("Message ID: ").strip()
    emoji      = inp("Emoji: ").strip()
    delay      = float(inp("Delay per token: ").strip() or "0.5")

    from urllib.parse import quote
    emoji_enc = quote(emoji)
    reacted   = 0

    for token in tokens:
        hdrs = discord_headers(token)
        r = requests.put(
            f"{DISCORD_API}/channels/{ch_id}/messages/{msg_id}/reactions/{emoji_enc}/@me",
            headers=hdrs, timeout=10
        )
        if r.status_code == 204:
            reacted += 1
            print(f"{G}[REACTED]{RESET} Token: {token[:25]}...")
        else:
            print(f"{R}[FAILED]{RESET} Token: {token[:25]}... | {r.status_code}")
        time.sleep(delay)

    success(f"Reacted: {reacted}/{len(tokens)}")
    pause()

# ============================================================
#           41. RANDOM USERNAME GENERATOR
# ============================================================

def username_generator():
    header("Random Username Generator")
    amount = int(inp("Amount: ").strip() or "10")
    prefix = inp("Prefix (optional): ").strip()
    suffix = inp("Suffix (optional): ").strip()
    length = int(inp("Random part length (default 6): ").strip() or "6")

    adjectives = ["Dark","Shadow","Phantom","Ghost","Silent","Rapid","Cyber","Neon",
                  "Apex","Ultra","Hyper","Storm","Frost","Blaze","Void","Quantum"]
    nouns      = ["Wolf","Shark","Eagle","Dragon","Tiger","Viper","Raven","Phoenix",
                  "Blade","Storm","Hunter","Reaper","Slayer","Knight","Specter","Ninja"]

    usernames = []
    for _ in range(amount):
        style = random.randint(1, 4)
        if   style == 1: mid = f"{random.choice(adjectives)}{random.choice(nouns)}"
        elif style == 2: mid = f"{random.choice(adjectives)}{''.join(random.choices(string.digits, k=3))}"
        elif style == 3: mid = ''.join(random.choices(string.ascii_lowercase, k=length))
        else:            mid = f"{random.choice(nouns)}{''.join(random.choices(string.digits, k=4))}"
        username = f"{prefix}{mid}{suffix}"
        usernames.append(username)
        print(f"  {G}{username}{RESET}")

    save = inp("\nSave? (y/n): ").strip().lower()
    if save == 'y':
        with open("usernames.txt", 'w') as f:
            f.write('\n'.join(usernames))
        success("Saved to usernames.txt")
    pause()

# ============================================================
#           42. DISCORD ACCOUNT CREATOR HELPER (Token Format)
# ============================================================

def discord_token_decoder():
    header("Discord Token Decoder")
    token = inp("Token: ").strip()

    parts = token.split('.')
    if len(parts) < 3:
        error("Invalid token format."); pause(); return

    try:
        # Part 1: User ID (base64)
        uid_b64 = parts[0]
        # Pad
        uid_b64 += '=' * (-len(uid_b64) % 4)
        uid = base64.b64decode(uid_b64).decode()
        info(f"User ID:     {uid}")

        # Part 2: Timestamp
        ts_b64 = parts[1]
        ts_b64 += '=' * (-len(ts_b64) % 4)
        ts_bytes = base64.b64decode(ts_b64 + '==')
        ts_int   = int.from_bytes(ts_bytes, 'big')
        dt       = datetime.datetime.utcfromtimestamp(ts_int + 1293840000)
        info(f"Created At:  {dt} UTC")

        # Part 3: HMAC
        info(f"HMAC Part:   {parts[2]}")

        # Account creation from ID
        try:
            iid = int(uid)
            acc_ts = ((iid >> 22) + 1420070400000) / 1000
            acc_dt = datetime.datetime.utcfromtimestamp(acc_ts)
            info(f"Account Created: {acc_dt} UTC")
        except Exception:
            pass

    except Exception as e:
        error(f"Decode error: {e}")
    pause()

# ============================================================
#           43. WEBHOOK EMBED BUILDER (Interactive)
# ============================================================

def webhook_embed_builder():
    header("Advanced Webhook Embed Builder")
    url = inp("Webhook URL: ").strip()

    embed: Dict[str, Any] = {}
    payload: Dict[str, Any] = {"embeds": [embed]}

    wh_user = inp("Webhook display name: ").strip()
    wh_av   = inp("Webhook avatar URL: ").strip()
    if wh_user: payload['username']   = wh_user
    if wh_av:   payload['avatar_url'] = wh_av

    content = inp("Message content (optional): ").strip()
    if content: payload['content'] = content

    embed['title']       = inp("Title: ").strip()
    embed['description'] = inp("Description: ").strip()
    embed['url']         = inp("Title URL: ").strip() or None

    color = inp("Color hex (e.g. ff4500): ").strip()
    try: embed['color'] = int(color.lstrip('#'), 16)
    except Exception: embed['color'] = 0x00ff00

    # Author
    author_name = inp("Author name: ").strip()
    if author_name:
        embed['author'] = {
            "name":     author_name,
            "icon_url": inp("Author icon URL: ").strip() or None,
            "url":      inp("Author URL: ").strip() or None
        }

    # Thumbnail & Image
    thumb = inp("Thumbnail URL: ").strip()
    img   = inp("Image URL: ").strip()
    if thumb: embed['thumbnail'] = {"url": thumb}
    if img:   embed['image']     = {"url": img}

    # Fields
    fields_count = int(inp("Number of fields (0-25): ").strip() or "0")
    embed['fields'] = []
    for i in range(min(fields_count, 25)):
        print(f"\n{Y}Field {i+1}:{RESET}")
        fname  = inp("  Name: ").strip()
        fval   = inp("  Value: ").strip()
        finlin = inp("  Inline? (y/n): ").strip().lower() == 'y'
        embed['fields'].append({"name": fname, "value": fval, "inline": finlin})

    # Footer
    footer = inp("\nFooter text: ").strip()
    if footer:
        embed['footer'] = {
            "text":     footer,
            "icon_url": inp("Footer icon URL: ").strip() or None
        }

    embed['timestamp'] = datetime.datetime.utcnow().isoformat()

    # Preview
    print(f"\n{Y}Payload preview:{RESET}")
    print(json.dumps(payload, indent=2)[:500] + "...")

    if inp("\nSend? (y/n): ").strip().lower() == 'y':
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code in [200, 204]:
            success("Embed sent!")
        else:
            error(f"Failed: {r.status_code} {r.text}")

    if inp("Save payload? (y/n): ").strip().lower() == 'y':
        save_to_file("embed_payload.json", json.dumps(payload, indent=2), 'w')
    pause()

# ============================================================
#           44. DISCORD PFPS MASS CHANGER
# ============================================================

def discord_pfp_changer():
    header("Discord PFP Mass Changer")
    token_file = inp("Token file: ").strip()
    tokens     = load_file(token_file)
    pfp_source = inp("(1) URL  (2) Local file: ").strip()

    if pfp_source == '1':
        url = inp("Image URL: ").strip()
        r   = requests.get(url)
        if r.status_code != 200:
            error("Cannot fetch image."); pause(); return
        img_b64 = base64.b64encode(r.content).decode()
        ext = url.split('.')[-1].lower() or 'png'
    else:
        path = inp("Image file path: ").strip()
        if not os.path.exists(path):
            error("File not found."); pause(); return
        with open(path, 'rb') as f:
            img_b64 = base64.b64encode(f.read()).decode()
        ext = path.split('.')[-1].lower() or 'png'

    avatar_data = f"data:image/{ext};base64,{img_b64}"

    for token in tokens:
        hdrs = discord_headers(token)
        pwd  = ""  # Some accounts require password - skip if needed
        r = requests.patch(f"{DISCORD_API}/users/@me",
                           headers=hdrs,
                           json={"avatar": avatar_data}, timeout=10)
        if r.status_code == 200:
            success(f"PFP changed | Token: {token[:25]}...")
        else:
            error(f"Failed | Token: {token[:25]}... | {r.status_code}")
        time.sleep(1)
    pause()

# ============================================================
#           45. HTTP REQUEST BUILDER
# ============================================================

def http_request_builder():
    header("HTTP Request Builder")
    method  = inp("Method (GET/POST/PUT/DELETE/PATCH): ").strip().upper()
    url     = inp("URL: ").strip()

    # Headers
    headers = {}
    print(f"\n{Y}Add headers (leave name blank to stop):{RESET}")
    while True:
        hname = inp("Header name: ").strip()
        if not hname: break
        hval  = inp(f"  {hname} value: ").strip()
        headers[hname] = hval

    # Body
    body = None
    if method in ['POST', 'PUT', 'PATCH']:
        body_type = inp("Body type (json/form/raw/none): ").strip().lower()
        if body_type == 'json':
            body_str = inp("JSON body: ").strip()
            try: body = json.loads(body_str)
            except Exception: body = {}
        elif body_type == 'form':
            body = {}
            while True:
                k = inp("Form key (blank to stop): ").strip()
                if not k: break
                v = inp(f"  {k} value: ").strip()
                body[k] = v
        elif body_type == 'raw':
            body = inp("Raw body: ").strip()

    # Proxy
    proxies = None
    use_proxy = inp("Use proxy? (y/n): ").strip().lower()
    if use_proxy == 'y':
        proxy = inp("Proxy (ip:port): ").strip()
        ptype = inp("Type (http/socks5): ").strip() or 'http'
        proxies = {"http": f"{ptype}://{proxy}", "https": f"{ptype}://{proxy}"}

    timeout = float(inp("Timeout (seconds, default 10): ").strip() or "10")

    try:
        if method == 'GET':
            r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        elif method == 'POST':
            if isinstance(body, dict):
                r = requests.post(url, headers=headers, json=body, proxies=proxies, timeout=timeout)
            else:
                r = requests.post(url, headers=headers, data=body, proxies=proxies, timeout=timeout)
        elif method == 'PUT':
            r = requests.put(url, headers=headers, json=body, proxies=proxies, timeout=timeout)
        elif method == 'DELETE':
            r = requests.delete(url, headers=headers, proxies=proxies, timeout=timeout)
        elif method == 'PATCH':
            r = requests.patch(url, headers=headers, json=body, proxies=proxies, timeout=timeout)
        else:
            error("Unknown method."); pause(); return

        separator()
        status_color = G if r.status_code < 300 else (Y if r.status_code < 400 else R)
        print(f"  {C}Status:{RESET}  {status_color}{r.status_code} {r.reason}{RESET}")
        print(f"  {C}Time:{RESET}    {r.elapsed.total_seconds():.3f}s")
        print(f"  {C}Size:{RESET}    {len(r.content)} bytes")
        print(f"\n{Y}Response Headers:{RESET}")
        for k, v in r.headers.items():
            print(f"  {C}{k}:{RESET} {v}")
        print(f"\n{Y}Response Body:{RESET}")
        try:
            print(json.dumps(r.json(), indent=2)[:2000])
        except Exception:
            print(r.text[:2000])
        separator()

        save = inp("Save response? (y/n): ").strip().lower()
        if save == 'y':
            save_to_file("http_response.txt",
                         f"Status: {r.status_code}\n{r.text}", 'w')
    except Exception as e:
        error(f"Request failed: {e}")
    pause()

# ============================================================
#           MAIN MENUS
# ============================================================

def discord_menu():
    while True:
        header("Discord Tools")
        print(f"  {G}[01]{RESET} Token Validator")
        print(f"  {G}[02]{RESET} Token Onliner")
        print(f"  {G}[03]{RESET} Token Info")
        print(f"  {G}[04]{RESET} Token Nuker")
        print(f"  {G}[05]{RESET} Token Cloner")
        print(f"  {G}[06]{RESET} Token Joiner")
        print(f"  {G}[07]{RESET} Token Leaver")
        print(f"  {G}[08]{RESET} Token Changer")
        print(f"  {G}[09]{RESET} Token Decoder")
        print(f"  {G}[10]{RESET} DM Spammer")
        print(f"  {G}[11]{RESET} Mass Token Spammer")
        print(f"  {G}[12]{RESET} Mass Message Deleter")
        print(f"  {G}[13]{RESET} Guild Spammer")
        print(f"  {G}[14]{RESET} Guild Nuker")
        print(f"  {G}[15]{RESET} Guild Creator")
        print(f"  {G}[16]{RESET} Guild Member Scraper")
        print(f"  {G}[17]{RESET} Server Scraper")
        print(f"  {G}[18]{RESET} Channel Creator")
        print(f"  {G}[19]{RESET} Invite Creator")
        print(f"  {G}[20]{RESET} Invite Info")
        print(f"  {G}[21]{RESET} Role Creator")
        print(f"  {G}[22]{RESET} Typing Indicator")
        print(f"  {G}[23]{RESET} Reaction Adder")
        print(f"  {G}[24]{RESET} Mass Reaction")
        print(f"  {G}[25]{RESET} Friend Adder")
        print(f"  {G}[26]{RESET} Custom Status Setter")
        print(f"  {G}[27]{RESET} PFP Changer")
        print(f"  {G}[28]{RESET} Nitro Generator + Checker")
        print(f"  {G}[29]{RESET} Bot Token Checker")
        print(f"  {R}[00]{RESET} ← Back")

        ch = inp("Choice: ").strip()
        actions = {
            '1':  discord_token_validator,
            '01': discord_token_validator,
            '2':  discord_token_onliner,
            '02': discord_token_onliner,
            '3':  discord_token_info,
            '03': discord_token_info,
            '4':  discord_token_nuker,
            '04': discord_token_nuker,
            '5':  discord_token_cloner,
            '05': discord_token_cloner,
            '6':  discord_token_joiner,
            '06': discord_token_joiner,
            '7':  discord_token_leaver,
            '07': discord_token_leaver,
            '8':  discord_token_changer,
            '08': discord_token_changer,
            '9':  discord_token_decoder,
            '09': discord_token_decoder,
            '10': discord_dm_spammer,
            '11': discord_mass_token_spammer,
            '12': discord_mass_delete,
            '13': discord_guild_spammer,
            '14': discord_guild_nuker,
            '15': discord_guild_creator,
            '16': discord_member_scraper,
            '17': discord_server_scraper,
            '18': discord_channel_creator,
            '19': discord_invite_creator,
            '20': discord_invite_info,
            '21': discord_role_creator,
            '22': discord_typing,
            '23': discord_reaction_adder,
            '24': discord_mass_reaction,
            '25': discord_friend_adder,
            '26': discord_custom_status,
            '27': discord_pfp_changer,
            '28': discord_nitro_gen,
            '29': discord_bot_checker,
            '00': None, '0': None
        }

        if ch in ('0', '00'):
            break
        action = actions.get(ch)
        if action:
            action()
        else:
            error("Invalid choice.")
            time.sleep(1)

def webhook_menu():
    while True:
        header("Webhook Tools")
        print(f"  {G}[1]{RESET} Webhook Spammer")
        print(f"  {G}[2]{RESET} Webhook Deleter")
        print(f"  {G}[3]{RESET} Webhook Info")
        print(f"  {G}[4]{RESET} Webhook Embed Sender")
        print(f"  {G}[5]{RESET} Webhook Multi-Sender")
        print(f"  {G}[6]{RESET} Webhook Checker")
        print(f"  {G}[7]{RESET} Advanced Embed Builder")
        print(f"  {G}[8]{RESET} Webhook Logger (HTTP Server)")
        print(f"  {R}[0]{RESET} ← Back")

        ch = inp("Choice: ").strip()
        wh_actions = {
            '1': discord_webhook_spammer,
            '2': discord_webhook_deleter,
            '3': discord_webhook_info,
            '4': discord_webhook_embed,
            '5': webhook_multi_sender,
            '6': webhook_checker,
            '7': webhook_embed_builder,
            '8': webhook_logger,
        }
        if ch == '0': break
        action = wh_actions.get(ch)
        if action: action()
        else: error("Invalid."); time.sleep(1)

def proxy_menu():
    while True:
        header("Proxy Tools")
        print(f"  {G}[1]{RESET} Proxy Scraper")
        print(f"  {G}[2]{RESET} Proxy Checker")
        print(f"  {G}[3]{RESET} Load Proxy Rotator")
        print(f"  {G}[4]{RESET} Get Next Proxy (Test)")
        print(f"  {R}[0]{RESET} ← Back")

        ch = inp("Choice: ").strip()
        if ch == '0': break
        elif ch == '1': proxy_scraper()
        elif ch == '2': proxy_checker()
        elif ch == '3': proxy_rotator_load()
        elif ch == '4':
            p = get_next_proxy()
            if p: success(f"Proxy: {p}")
            else: error("No proxies loaded.")
            pause()
        else: error("Invalid."); time.sleep(1)

def other_tools_menu():
    while True:
        header("Other Tools")
        print(f"  {G}[1]{RESET} IP Lookup")
        print(f"  {G}[2]{RESET} Port Scanner")
        print(f"  {G}[3]{RESET} String Tools")
        print(f"  {G}[4]{RESET} HTTP Request Builder")
        print(f"  {G}[5]{RESET} Username Generator")
        print(f"  {R}[0]{RESET} ← Back")

        ch = inp("Choice: ").strip()
        if   ch == '0': break
        elif ch == '1': ip_lookup()
        elif ch == '2': port_scanner()
        elif ch == '3': string_tools()
        elif ch == '4': http_request_builder()
        elif ch == '5': username_generator()
        else: error("Invalid."); time.sleep(1)

def main_menu():
    # Check/install dependencies
    try:
        import colorama
        import requests
        import websocket
        import socks
    except ImportError:
        print("Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install",
                        "requests", "colorama", "websocket-client",
                        "PySocks"], check=False)
        init(autoreset=True)

    while True:
        banner()
        print(f"  {C}[1]{RESET} {Y}Discord Tools{RESET}   {DIM}(30+ tools){RESET}")
        print(f"  {C}[2]{RESET} {Y}Webhook Tools{RESET}   {DIM}(8 tools){RESET}")
        print(f"  {C}[3]{RESET} {Y}Proxy Tools{RESET}     {DIM}(4 tools){RESET}")
        print(f"  {C}[4]{RESET} {Y}Other Tools{RESET}     {DIM}(5 tools){RESET}")
        print(f"  {R}[0]{RESET} Exit")
        print()

        ch = inp("Choice: ").strip()
        if   ch == '1': discord_menu()
        elif ch == '2': webhook_menu()
        elif ch == '3': proxy_menu()
        elif ch == '4': other_tools_menu()
        elif ch == '0':
            warn("Goodbye!")
            sys.exit(0)
        else:
            error("Invalid choice.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()