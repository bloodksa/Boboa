
import os
import json
import subprocess

CONFIG_FILE = "bots_config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("Configuration file not found.")
        return []
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file).get('bots', [])

def add_bot(name, description, entry_point, github_repo=None):
    bots = load_config()
    new_bot = {
        "name": name,
        "description": description,
        "entry_point": entry_point,
        "github_repo": github_repo
    }
    bots.append(new_bot)
    save_config(bots)
    if github_repo:
        clone_repo(github_repo, entry_point)
    print(f"Bot '{name}' added successfully.")

def save_config(bots):
    with open(CONFIG_FILE, 'w') as file:
        json.dump({"bots": bots}, file, indent=4)

def clone_repo(repo_url, target_dir):
    print(f"Cloning repository {repo_url} into {target_dir}...")
    subprocess.run(["git", "clone", repo_url, target_dir], check=True)
    print("Repository cloned successfully.")

def list_bots():
    bots = load_config()
    print("Registered Bots:")
    for bot in bots:
        print(f"- {bot['name']}: {bot['description']} (Repo: {bot.get('github_repo', 'Local')})")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bot Management Script")
    parser.add_argument("--add", nargs=4, metavar=("NAME", "DESCRIPTION", "ENTRY_POINT", "REPO_URL"), help="Add a new bot")
    parser.add_argument("--list", action="store_true", help="List all registered bots")
    args = parser.parse_args()

    if args.add:
        add_bot(*args.add)
    elif args.list:
        list_bots()
    else:
        print("Use --help for available options.")
