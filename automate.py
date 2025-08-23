####
# automate.py - Automated scraping of group walls, for archival purposes.
# Garry – August 22nd, 2025.
# Licensed under GNU General Public License v3.0
# Revision Development 03

# Revision History:
#   Revision Development 01 - Initial development revision
#   Revision Development 02 - Add arguments for extensive functionality
#   Revision Development 03 - Update file process to use folders
#   Revision 1.0 - Initial release
SCRIPT_VERSION = "RGWA automate.py Revision 1.0"
####

# Thank you for using this automation script! Please make sure to read the documentation on https://github.com/ReinoScreech/roblox-wall-archive/blob/main/README.md
# for a clear understanding on how things work here.

import requests
import datetime
import time
import sys
import os
import argparse

# ANSI Codes
ERROR = "\033[91m"
SUCCESS = "\033[92m"
WARNING = "\033[93m"
INFO = "\033[94m"
RESET = "\033[0m"

# Arguments for the script.
def parse_args():
    parser = argparse.ArgumentParser(description="Roblox Group Wall Archiver - Automation Process")
    parser.add_argument(
        "--groupid",
        type=int,
        required=True,
        help="The numeric ID of the group. You can find this in a Roblox URL."
    )
    parser.add_argument(
        "--groupname",
        type=str,
        required=True,
        help="The name of the group, for file naming."
    )
    parser.add_argument(
        "--roblosecurity", 
        help="(OPTIONAL) Your .ROBLOSECURITY cookie. WARNING: This gives full access to your Roblox account!"
    )
    parser.add_argument(
        "--compact",
        help="(OPTIONAL) Formats all posts into one line at a time.",
        action="store_true"
    )
    return parser.parse_args()

try:
    parse_args()
except SystemExit:
    print(f"\n{WARNING}To use this program, you must add the --groupid and --groupname arguments.\nFor a list of arguments. Run this program with --h or --help.{RESET}\nCheck out the documentation at https://github.com/ReinoScreech/roblox-wall-archive/blob/main/README.md")
    sys.exit(0)

marg = parse_args()
GROUP_ID = marg.groupid
GROUP_NAME = marg.groupname
OUTPUT_FILE = f"{GROUP_NAME}_{GROUP_ID}.txt"

WALL_URL = f"https://groups.roblox.com/v2/groups/{GROUP_ID}/wall/posts"
RANK_URL = "https://groups.roblox.com/v2/users/{userId}/groups/roles"

rank_cache = {}



# This is redundant.
def get_user_rank_name(user_id):
    """Return rank name for user in group, with caching."""
    if user_id == 0:
        return "Unknown"
    if user_id in rank_cache:
        return rank_cache[user_id]

    print(f"  Fetching rank for user {user_id}...")
    r = requests.get(RANK_URL.format(userId=user_id))
    if r.status_code != 200:
        rank_cache[user_id] = "Unknown"
        return "Unknown"

    data = r.json().get('data', [])
    role_name = "Unknown"
    for g in data:
        if g['group']['id'] == GROUP_ID:
            role_name = g['role']['name']
            break

    rank_cache[user_id] = role_name
    time.sleep(1)
    return role_name

# Make a GET request to the API and provide warnings if an error code occurs.
def retr_api(url, params=None, headers=None, ret_max=5, cd=120):
    for attempt in range(1, ret_max + 1):
        r = requests.get(url, params=params, headers=headers)
        if r.status_code == 403:
            print(f"{ERROR}This group likely its wall disabled from view for users not in group or your rank does not allow viewing. To continue, you will need to append your token using the argument, --roblosecurity to scrape under your account credentials (not recommended) or do a manual scrape.\nIf you are not able to read this group's wall, please contact the group holder.{RESET}")
            sys.exit(0)
        elif r.status_code == 429:
            print(f"{ERROR}The API's rate-limit has been reached. {RESET}Trying again in {cd} seconds. ({attempt}/{ret_max}){RESET}\nPress {INFO}Ctrl+C{RESET} if you would like to exit at any time. (Note: All requests will be lost!)")
            time.sleep(cd)
            continue
        elif r.status_code != 200:
            print(f"{ERROR}The API returned an unexpected error:{RESET}", r.status_code)
            conf = input("\nContinue anyway? (y/n): ").strip().lower()
            if conf == "y":
                continue
            else:
                break

        return r.json()

# Fetch wall posts from the API
def fetch_wall_posts(rs=None, cmp=False):
    """Fetch all group wall posts sorted descending."""
    headers = {
        "Accept": "application/json"
    }
    # If the user applied .ROBLOSECURITY, use that for the header.
    if rs:
        headers = {
        "Accept": "application/json",
        "Cookie": f".ROBLOSECURITY={rs}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }

    params = {"limit": 100, "sortOrder": "Desc"}
    posts = []
    page_count = 0

    print("Fetching group wall posts...")

    while True:


        data = retr_api(WALL_URL, params=params, headers=headers)
        if not data:
            break

        page_count += 1
        print(f"  Retrieved page {page_count} with {len(data['data'])} posts. Next page: {data.get('nextPageCursor')}")

        for post in data['data']:
            poster = post.get('poster') or {}
            user_poster = poster.get('user') or {}
            role_data = poster.get('role') or {}
            display_name = user_poster.get('displayName', "Unknown")
            user_id = user_poster.get('userId', 0)
            role_name = role_data.get('name')
            content = post.get('body', '')
            created = post.get('created')
            dt = datetime.datetime.fromisoformat(created.replace("Z", "+00:00")).astimezone(datetime.timezone.utc)
            date_posted = dt.strftime("%Y-%m-%d")
            time_posted = dt.strftime("%H:%M")

            # Old group walls have broken posts for some reason, so fallbacks and this warning is here so that user_poster doesn't error out.
            if not poster:
                print(f"{WARNING}Poster info missing for post ID {post.get('id')} {RESET}")

#            print(f"Debug - {display_name}, {user_id}, {post.get('created')}")

            if not role_name:
                role_name = get_user_rank_name(user_id)

            if cmp:
                formatted_post = (
                f"{display_name} ({user_id}): {content} | {role_name} | {date_posted} {time_posted} UTC"
                )
            else:
                formatted_post = (
                f"{display_name} ({user_id})\n"
                f"{content}\n\n"
                f"{role_name} | {date_posted} | {time_posted} UTC\n"
                )            
            
            posts.append(formatted_post)

        if data.get('nextPageCursor'):
            params['cursor'] = data['nextPageCursor']
            time.sleep(1)  # cooldown per page
        else:
            break

    print(f"\nFinished fetching posts. Total pages: {page_count}")
    return posts, page_count

# Save the contents to its own folder.
def save_file(posts, page_count):
    if not posts:
        print(f"{WARNING}It doesn't seem like this group wall, {GROUP_ID}, has any posts.{RESET}")
        return

    # This doesn't even do anything it just falls back to Unknown every time!

    # Get first and last post dates
    # Since posts are descending, first post = last element.

    # First post:
    lines = posts[-1].split("\n")  # posts[-1] = oldest
    last_line = lines[-1] if lines else ""
    parts = last_line.split("|")
    if len(parts) >= 3:  # RoleName | YYYY-MM-DD | HH:MM UTC
        first_post_date = parts[1].strip()
        first_post_time = parts[2].strip()
    else:
        first_post_date = "Unknown"
        first_post_time = "Unknown"

    # Last post:
    lines = posts[0].split("\n")  # posts[0] = newest
    last_line = lines[-1] if lines else ""
    parts = last_line.split("|")
    if len(parts) >= 3:
        last_post_date = parts[1].strip()
        last_post_time = parts[2].strip()
    else:
        last_post_date = "Unknown"
        last_post_time = "Unknown"

    # Start writing the results
    print(f"\nWriting results...")

    BASE = "Archives"
    os.makedirs(BASE, exist_ok=True)

    GROUP_FOLDER = f"{GROUP_NAME}_{GROUP_ID}"
    group_path = os.path.join(BASE, GROUP_FOLDER)
    os.makedirs(group_path, exist_ok=True)

    arch_path    = os.path.join(group_path, f"{GROUP_FOLDER}.txt")
    license_path = os.path.join(group_path, "LICENSE.txt")
    
    lic_text = """~~~~~~~~~~
    This file was automatically generated by RGWA automate.py
    It is licensed under the CC BY-ND 4.0 (Attribution-NoDerivatives) license.
    https://creativecommons.org/licenses/by-nd/4.0/

    You are free to share this file, but you may not
    modify, change, or remix its contents unless explicitly labeled.
    This license is put in place to ensure posts are preserved exactly 
    as they are written to prevent attempts at defamation, harassment, 
    or misrepresentation.

    This automated capture is created to be intended as a factual 
    historical record and any redistributed or altered versions must 
    clearly indicate they are unofficial to avoid problems stated
    above.
    
    Thank you for your cooperation!
~~~~~~~~~~"""
    if not os.path.exists(license_path):
        with open(license_path, "w", encoding="utf-8") as f:
            f.write(lic_text)

    # Write the archive file
    with open(arch_path, "w", encoding="utf-8") as f:
        header_text = (
            f"{SCRIPT_VERSION}\n\n"
            "NOTE:\n"
            "This archive is an automated capture of a Roblox group wall.\n"
            "It is intended as a factual historical record. Any redistributed\n"
            "or altered versions must clearly indicate they are unofficial\n"
            f"to avoid misleading or defaming individuals.\nPlease read the LICENSE.txt file for more information.\n\n"
            f"This is the GROUP WALL for {GROUP_NAME} - "
            f"https://www.roblox.com/communities/{GROUP_ID}/{GROUP_NAME}#!/about\n\n"
            f"Archived {datetime.datetime.now(datetime.timezone.utc).strftime('%b %d, %Y, %I:%M %p')} UTC\n\n"
            "Date and Time presumably set to UTC.\n\n"
            "INFORMATION:\n"
            "This is AUTOMATED ARCHIVE. You should have a copy of the automated script used for this process.\n"
            f"About {page_count} page(s) have been archived in this wall.\n"
            f"The first message was @ {first_post_date} | {first_post_time}\n"
            f"The last message was @ {last_post_date} | {last_post_time}\n\n"
            "CONTENT:\n"
        )
        f.write(header_text)

        # Apply posts to the file
        for post in posts:
            f.write(post + "\n")

    print(f"\n{SUCCESS}Archival process completed! Your new file is located in the path\n{arch_path}{RESET}")

# Main initialization process.
def main():
    args = parse_args()
    roblosecurity = args.roblosecurity
    compact = args.compact



    if roblosecurity:
        if sys.platform.startswith('win'):
            os.system('cls')
        else:
            os.system('clear')

        print(f"{RESET}{INFO}{SCRIPT_VERSION} © 2025 Garry Brown\nThis program is licensed under GNU General Public License v3.0. \nGenerated files are licensed under CC-BY-ND-4.0.{RESET}\n\nThis script retrieves posts from a group's wall to preserve once walls are deprecated and removed.\nPlease remember, this script is for archival purposes only! Do not use it for malicious purposes.\n")
        print(f"{WARNING}WARNING: You are providing your .ROBLOSECURITY cookie.")
        print(f"{WARNING}This gives FULL access to your account. Use at your own risk!")
        print(f"If someone else gave you this cookie or you are unsure, DO NOT proceed.{RESET}")

        conf = input("\nAre you sure you want to continue? (y/n): ").strip().lower()
        if conf != "y":
            sys.exit(0)

    print(f"\nStarting in 10 seconds. Press {INFO}Ctrl+C{RESET} to cancel...\n")
    # Start a countdown from 10 seconds and start fetch_wall_posts when it reaches zero.
    try:
        for i in range(10, 0, -1):
            print(f"{i}...", end=" ", flush=True)
            time.sleep(1)

        print(f"\nPreparing to retrieve posts from {GROUP_NAME} ({GROUP_ID}). This may take a while, so please be patient.")
        posts, page_count = fetch_wall_posts(roblosecurity, compact) # Defaults to None if it did not get an input
        save_file(posts, page_count)
    except KeyboardInterrupt:
        print(f"\n{RESET}Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    
    print(f"{RESET}{INFO}{SCRIPT_VERSION} © 2025 Garry Brown\nThis program is licensed under GNU General Public License v3.0. \nGenerated files are licensed under CC-BY-ND-4.0.{RESET}\n\nThis script retrieves posts from a group's wall to preserve once walls are deprecated and removed.\nPlease remember, this script is for archival purposes only! Do not use it for malicious purposes.\n")
    main()

