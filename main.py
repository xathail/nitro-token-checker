import concurrent.futures, requests, datetime, os
proxy = {'http': 'http://user:pass@host:port','https': 'http://user:pass@host:port'} # Replace user:pass@host:port with your proxy.

def main():
    tokens = open("tokens.txt", "r").readlines()
    tokens = [token.rstrip() for token in tokens]
    num_threads = int(input("Enter the number of threads to use: "))
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        start = datetime.datetime.now()
        session = requests.Session()
        for token in tokens:
            futures.append(executor.submit(updatedChecker, session, token))
        for future in concurrent.futures.as_completed(futures):
            future.result()
        session.close()
    end = datetime.datetime.now()
    print("Successfully checked",len(tokens),"tokens in", end-start)

def updatedChecker(session, token):
    now = datetime.datetime.now(datetime.timezone.utc)
    directory = now.strftime("%d-%m-%Y %H;%M")
    os.makedirs(directory, exist_ok=True)
    headers = {"Authorization": token}
    try:
        response = session.get("https://discord.com/api/v9/users/@me", headers=headers, proxies=proxy)
        response.raise_for_status() 
        user = response.json()
    except (requests.exceptions.HTTPError, ValueError):
        print(f"\033[31m{token}")
        with open(f"{directory}/Invalids.txt", "a") as f:
            f.write(f"{token}\n")
        return
    
    if user["premium_type"] == 0:
        print(f"\033[32m{token}")
        with open(f"{directory}/NoNitro.txt", "a") as f:
            f.write(f"{token} = {user['username']}#{user['discriminator']}\n")
    elif user["premium_type"] == 2:
        try:
            response = session.get("https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots", headers=headers, proxies=proxy)
            response.raise_for_status()
            boostCheck = response.json()
        except requests.exceptions.HTTPError:
            boostCheck = []
        availableBoosts = 0
        for nitro_token in boostCheck:
            cooldownEnds = nitro_token.get('cooldown_ends_at')
            if cooldownEnds is None or datetime.datetime.fromisoformat(cooldownEnds.split('+')[0] + '+00:00').replace(tzinfo=datetime.timezone.utc) <= now:
                availableBoosts += 1
        p = '| Server Boosted: None '
        nitroExpires = ""
        ok = str(availableBoosts)+' '+p
        if boostCheck and boostCheck[0]['premium_guild_subscription'] is not None:
            p = f"| Server Boosted: {boostCheck[0]['premium_guild_subscription']['guild_id']} "
            try:
                response = session.get("https://discord.com/api/v9/users/@me/billing/subscriptions", headers=headers, proxies=proxy)
                response.raise_for_status()
                nitroCheck = response.json()
                nitroExpires = '| Expires: ' + datetime.datetime.fromisoformat(nitroCheck[0]['trial_ends_at']).replace(tzinfo=datetime.timezone.utc).strftime('%d-%m-%Y %H:%M')
                ok = str(availableBoosts)+' '+(nitroExpires)+' '+(p)
            except requests.exceptions.HTTPError:
                pass   
        print(f"\033[32m{token}")
        with open(f"{directory}/NitroBoostTokens.txt", "a") as f:
            f.write(f"{token} | Transferrable Boosts: {ok} | {user['username']}#{user['discriminator']}\n")
    else:
        print(f"\033[32m{token}")
        with open(f"{directory}/NitroBasicTokens.txt", "a") as f:
            f.write(f"{token} | {user['username']}#{user['discriminator']}\n")

main()
