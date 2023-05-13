import concurrent.futures, requests, datetime;from colorama import Fore, Back, Style

def check_token(token):
    availableBoosts = 0
    now = datetime.datetime.now(datetime.timezone.utc)
    response = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token}) 
    if response.status_code == 200: 
        user = response.json()
        if user["premium_type"] != 0: 
            response = requests.get("https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots", headers={"Authorization": token}) # check available boosts
            boostCheck = response.json()
            for nitroToken in boostCheck:
                if 'cooldown_ends_at' in nitroToken:
                    if nitroToken['cooldown_ends_at'] == None: 
                        availableBoosts += 1
                        continue
                    else: 
                        cooldownEndStr = nitroToken['cooldown_ends_at'].split('+')[0] + '+00:00' 
                        cooldownEnds = datetime.datetime.fromisoformat(cooldownEndStr)
                        if cooldownEnds <= now:  
                            availableBoosts += 1        
        print(Fore.GREEN + token)
        f=open("valids.txt", "a")
        f.write(f"{token} | Boosts: {availableBoosts} = {user['username']}#{user['discriminator']}\n")
    else: 
        print(Fore.RED + token)
        f=open("invalids.txt", "a")
        f.write(f"{token}\n")
    return

def main():
    tokens = open("tokens.txt", "r").readlines() 
    tokens = [token.rstrip() for token in tokens] 
    num_threads = int(input("Enter the number of threads to use: "))

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for token in tokens:
            futures.append(executor.submit(check_token, token))

        for future in concurrent.futures.as_completed(futures):
            future.result()

    print("Successfully checked",len(tokens),"tokens")

main()
