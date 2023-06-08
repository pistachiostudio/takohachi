import json
import re
import socket
from collections import OrderedDict

import requests
import urllib3

"""
Thanks! https://github.com/DarkPotatoKing/valostore-py
"""

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Auth:
    def __init__(self, auth):
        self.username = auth["username"]
        self.password = auth["password"]

    def authenticate(self):
        # More on the topic: https://stackoverflow.com/questions/62684468/pythons-requests-triggers-cloudflares-security-while-urllib-does-not

        # grab the address using socket.getaddrinfo
        answers = socket.getaddrinfo("auth.riotgames.com", 443)
        (family, type, proto, canonname, (address, port)) = answers[0]

        headers = OrderedDict(
            {
                "Accept-Encoding": "gzip, deflate, br",
                "Host": "auth.riotgames.com",
                "User-Agent": "RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)",
            }
        )

        session = requests.session()
        session.headers = headers

        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
        }
        r = session.post(
            f"https://{address}/api/v1/authorization",
            json=data,
            headers=headers,
            verify=False,
        )

        # print(r.text)
        data = {"type": "auth", "username": self.username, "password": self.password}
        r = session.put(
            f"https://{address}/api/v1/authorization",
            json=data,
            headers=headers,
            verify=False,
        )
        pattern = re.compile(
            "access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)"
        )
        data = pattern.findall(r.json()["response"]["parameters"]["uri"])[0]
        access_token = data[0]
        # print('Access Token: ' + access_token)

        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Host": "entitlements.auth.riotgames.com",
            "User-Agent": "RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)",
            "Authorization": f"Bearer {access_token}",
        }
        r = session.post(
            "https://entitlements.auth.riotgames.com/api/token/v1",
            headers=headers,
            json={},
        )
        entitlements_token = r.json()["entitlements_token"]
        # print('Entitlements Token: ' + entitlements_token)

        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Host": "auth.riotgames.com",
            "User-Agent": "RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)",
            "Authorization": f"Bearer {access_token}",
        }

        r = session.post("https://auth.riotgames.com/userinfo", headers=headers, json={})
        user_id = r.json()["sub"]
        # print('User ID: ' + user_id)
        headers["X-Riot-Entitlements-JWT"] = entitlements_token
        del headers["Host"]
        session.close()
        return user_id, headers, {}


def pretty_print(data):
    print(json.dumps(data, indent=4, sort_keys=True))


def get_bundles(skins_data, bundles_data, weapons_data):
    bundles = []

    if skins_data["FeaturedBundle"]:
        bundles = skins_data["FeaturedBundle"]["Bundles"]

    for bundle in bundles:
        # bundle_id = bundle["DataAssetID"]
        # info = [i for i in bundles_data if i["uuid"] == bundle_id][0]
        # bundle_price = sum([i["DiscountedPrice"] for i in bundle["Items"]])

        for item in bundle["Items"]:
            uuid = item["Item"]["ItemID"]
            try:
                item_name = [i for i in weapons_data if i["uuid"] == uuid][0]["displayName"]
                item_price: int = int(item["BasePrice"])
                bundle_offer = f"{item_name} ({item_price:,})"
            except Exception:
                continue
    return bundle_offer


def get_data(user_id, headers, region):
    skins_data = requests.get(
        f"https://pd.{region}.a.pvp.net/store/v2/storefront/{user_id}", headers=headers
    )
    skins_data = skins_data.json()

    bundles_data = requests.get("https://valorant-api.com/v1/bundles")
    bundles_data = bundles_data.json()["data"]

    weapons_data = requests.get("https://valorant-api.com/v1/weapons/skinlevels")
    weapons_data = weapons_data.json()["data"]

    offers_data = requests.get(f"https://pd.{region}.a.pvp.net/store/v1/offers", headers=headers)
    offers_data = offers_data.json()["Offers"]

    return skins_data, bundles_data, weapons_data, offers_data


def get_skins(skins_data, weapons_data, offers_data):
    skins = skins_data["SkinsPanelLayout"]["SingleItemOffers"]

    prices = {}
    for offer in offers_data:
        for key in offer["Cost"]:
            val = offer["Cost"][key]
            prices[offer["OfferID"]] = val

    result = []
    for uuid in skins:
        skin = [i for i in weapons_data if i["uuid"] == uuid][0]
        skin_name = skin["displayName"]
        skin_price = int(prices[uuid])
        skin_image = skin["displayIcon"]
        shop_offer = f"[{skin_name}]({skin_image}) ({skin_price:,})"
        result.append(shop_offer)

    return result


def get_night_market(skins_data, weapons_data):
    if not skins_data["BonusStore"]:
        return

    night_market = skins_data["BonusStore"]["BonusStoreOffers"]

    nm_result = []
    for item in night_market:
        uuid = item["Offer"]["Rewards"][0]["ItemID"]
        skin_price = int([item["DiscountCosts"][i] for i in item["DiscountCosts"]][0])
        skin = [i for i in weapons_data if i["uuid"] == uuid][0]
        skin_name = skin["displayName"]
        # skin_image = skin["displayIcon"]
        nm_offer = f"{skin_name} ({skin_price:,})"
        nm_result.append(nm_offer)

    return nm_result
