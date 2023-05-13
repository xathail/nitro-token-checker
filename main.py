import concurrent.futures, requests, datetime, os
proxy = {'http': 'ENTER PROXY HERE','https': 'ENTER PROXY HERE'}

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
    directory = now.strftime("%d-%m-%Y %H:%M")
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
            boost_check = response.json()
        except requests.exceptions.HTTPError:
            boost_check = []
        available_boosts = 0
        for nitro_token in boost_check:
            cooldown_ends_at = nitro_token.get('cooldown_ends_at')
            if cooldown_ends_at is None or datetime.datetime.fromisoformat(cooldown_ends_at.split('+')[0] + '+00:00').replace(tzinfo=datetime.timezone.utc) <= now:
                available_boosts += 1
        nitro_expires = "Never"
        p = '| Server Boosted: None '
        if boost_check and boost_check[0]['premium_guild_subscription'] is not None:
            p = f"| Server Boosted: {boost_check[0]['premium_guild_subscription']['guild_id']} "
            try:
                response = session.get("https://discord.com/api/v9/users/@me/billing/subscriptions", headers=headers, proxies=proxy)
                response.raise_for_status()
                nitro_check = response.json()
                nitro_expires = datetime.datetime.fromisoformat(nitro_check[0]['trial_ends_at']).replace(tzinfo=datetime.timezone.utc).strftime('%d-%m-%Y %H:%M')
            except requests.exceptions.HTTPError:
                pass
        try:    
            print(f"\033[32m{token}")
            with open(f"{directory}/BoostTokens.txt", "a") as f:
                f.write(f"{token} | Available Boosts: {available_boosts} | Expires: {nitro_expires} {p} | {user['username']}#{user['discriminator']}\n")
        except:
            print(f"\033[32m{token}")
            with open(f"{directory}/BoostTokens.txt", "a") as f:
                f.write(f"{token} | Boosts: {available_boosts} | Expires: Never {p} | {user['username']}#{user['discriminator']}\n")
    else:
        print(f"\033[32m{token}")
        with open(f"{directory}/NitroTokens.txt", "a") as f:
            f.write(f"{token} | {user['username']}#{user['discriminator']}\n")

main()