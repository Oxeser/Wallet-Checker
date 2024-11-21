import os
import time
from concurrent.futures import ThreadPoolExecutor
from termcolor import colored
import pyfiglet
import requests
from mnemonic import Mnemonic
from bip32utils import BIP32Key
import subprocess

API_URL = "https://blockchain.info/balance"
found_count = 0
attempt_count = 0
rich_addresses = []

GITHUB_REPO_URL = "https://github.com/Oxeser/Wallet-Checker"

def update_from_github():
    print(colored("Checking for updates from GitHub...\n", "cyan"))
    try:
        if not os.path.exists(".git"):
            print(colored("This folder is not a Git repository. Skipping update...", "red"))
            return
        
        
        subprocess.run(["git", "fetch"], check=True)
        
        local_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
        remote_commit = subprocess.check_output(["git", "rev-parse", "origin/main"]).strip()
        
        if local_commit != remote_commit:
            print(colored("Updates found! Pulling latest changes...", "yellow"))
            subprocess.run(["git", "pull"], check=True)
            print(colored("Successfully updated to the latest version. Please restart the program.", "green"))
            exit()
        else:
            print(colored("Already up to date.", "green"))
    except Exception as e:
        print(colored(f"Error while updating: {e}", "red"))

def load_rich_list_from_file(file_path="btc.txt"):
    global rich_addresses
    try:
        with open(file_path, "r") as f:
            rich_addresses = [line.strip() for line in f.readlines() if line.strip()]
        print(colored(f"Loaded {len(rich_addresses)} addresses from {file_path}.", "green"))
    except FileNotFoundError:
        print(colored(f"Error: {file_path} not found. Ensure the file exists in the directory.", "red"))
        rich_addresses = []

def check_balance(address, mnemonic):
    global found_count
    try:
        response = requests.get(API_URL, params={"active": address})
        response.raise_for_status()
        data = response.json()
        balance = float(data[address]["final_balance"]) / 1e8
        if balance > 0:
            found_count += 1
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            output = (
                f"{current_time} | "
                f"Found: {colored(found_count, 'green')} | "
                f"Attempt: {colored(attempt_count, 'yellow')} | "
                f"Address: {colored(address, 'cyan')} | "
                f"Balance: {colored(balance, 'red')} BTC"
            )
            print(output)
            save_to_file(mnemonic, address, balance)
            return True
    except Exception:
        pass
    return False

def mnemonic_to_address(mnemonic):
    mnemo = Mnemonic("english")
    seed = mnemo.to_seed(mnemonic)
    bip32_key = BIP32Key.fromEntropy(seed)
    address = bip32_key.Address()
    return address

def generate_mnemonic(word_count=12):
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=128)

def save_to_file(mnemonic, address, balance):
    with open("founds.txt", "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | Mnemonic: {mnemonic}\n")
        f.write(f"Address: {address}\nBalance: {balance} BTC\n\n")

def process_mnemonic(mnemonic, target_address=None):
    global attempt_count
    attempt_count += 1
    address = mnemonic_to_address(mnemonic)
    if target_address and address != target_address:
        return
    found = check_balance(address, mnemonic)
    if not found:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(
            f"{current_time} | "
            f"Found: {colored(found_count, 'green')} | "
            f"Attempt: {colored(attempt_count, 'yellow')} | "
            f"Address: {colored(address, 'cyan')} | "
            f"Balance: {colored(0, 'red')} BTC"
        )

def wallet_checker(rich_list_mode=False, custom_file=None):
    print(colored("Starting Wallet Checker...\n", "cyan"))
    time.sleep(1)
    if rich_list_mode:
        if custom_file:
            load_rich_list_from_file(custom_file)
        else:
            load_rich_list_from_file()
        if not rich_addresses:
            print(colored("Rich list is empty or could not be loaded. Exiting...", "red"))
            return

    num_workers = 15
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        if rich_list_mode:
            for address in rich_addresses:
                mnemonic = generate_mnemonic(12)
                executor.submit(process_mnemonic, mnemonic, target_address=address)
        else:
            while True:
                mnemonics = [generate_mnemonic(12) for _ in range(num_workers)]
                executor.map(process_mnemonic, mnemonics)

def view_wallets():
    print(colored("\nFound Wallets:\n", "cyan", attrs=["bold"]))
    try:
        with open("founds.txt", "r") as f:
            content = f.read()
            if content.strip():
                print(colored(content, "yellow"))
            else:
                print(colored("No wallets found yet.", "red"))
    except FileNotFoundError:
        print(colored("No wallets found yet.", "red"))
    input(colored("\nPress any key to continue...", "green"))

def exit_program():
    print(colored("\nExiting...", "red"))
    time.sleep(1)
    exit()

def main_menu():
    while True:
        os.system("clear")
        logo = pyfiglet.figlet_format("Wallet Checker")
        print(colored(logo, "blue", attrs=["bold"]))
        print(colored("1. Start Wallet Checker", "cyan"))
        print(colored("2. Start Wallet Checker with Rich List", "cyan"))
        print(colored("3. View Found Wallets", "cyan"))
        print(colored("4. Exit", "red"))
        choice = input(colored("\nMake your choice (1/2/3/4): ", "green"))
        if choice == "1":
            wallet_checker()
        elif choice == "2":
            custom_file = input(colored("Enter the path to your rich list file (leave empty to use default): ", "yellow")).strip()
            wallet_checker(rich_list_mode=True, custom_file=custom_file if custom_file else None)
        elif choice == "3":
            view_wallets()
        elif choice == "4":
            exit_program()
        else:
            print(colored("Invalid choice. Please try again.", "red"))
            time.sleep(1)

if __name__ == "__main__":
    update_from_github()
    main_menu()
