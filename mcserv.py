import requests
import json
import re
import sys
import yaml


def login(url_):
    url = url_ + "/api/auth"
    payload = {
        "username": config("login"),
        "password": config("pass")
    }
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    return json.loads(response.text)["jwt"]


def get_container_id(url_, token):
    url = url_ + "/api/endpoints/2/docker/containers/json"

    querystring = {"all": "true"}

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Authorization": "Bearer " + token
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    i = 0
    while True:
        if re.search("itzg/minecraft-server*", json.loads(response.text)[i]['Image']):
            return json.loads(response.text)[i]['Id']
        i += 1


def get_state(url_, token):
    url = url_ + "/api/endpoints/2/docker/containers/" + get_container_id(url_, token) + "/json"

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Authorization": "Bearer " + token
    }

    response = requests.request("GET", url, headers=headers)

    if re.search("running", json.loads(response.text)['State']['Status']):
        return True
    else:
        return False


def start(url_, token):
    url = url_ + "/api/endpoints/2/docker/containers/" + get_container_id(url_, token) + "/start"

    payload = {}

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Authorization": "Bearer " + token
    }

    if get_state(url_, token):
        print("serwer już działa")
    else:
        requests.request("POST", url, json=payload, headers=headers)
        print("serwer uruchamia się")


def stop(url_, token):
    url = url_ + "/api/endpoints/2/docker/containers/" + get_container_id(url_, token) + "/stop"

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Authorization": "Bearer " + token
    }

    if get_state(url_, token):
        requests.request("POST", url, headers=headers)
        print("serwer wyłącza się")
    else:
        print("serwer jest już wyłączony")


def config(object):
    with open("conf.yaml", "r") as config_file:
        cfg = yaml.safe_load(config_file)

    return cfg[object]

def menu():
    url = config("portainer_url")
    jwt = login(url)

    print("\n")

    if get_state(url, jwt):
        print("Aktualny stan serwera mc: serwer Działa")
    else:
        print("Aktualny stan serwera mc: serwer Wyłączony")

    print("\n")

    print("co chcesz zrobić")
    print("aby włączyć naciśnij 1")
    print("aby wyłączyć naciśnij 2")
    print("aby wyjść naciśnij q")

    while True:
        char = sys.stdin.read(1)
        if char == '1':
            start(url, jwt)
        if char == '2':
            stop(url, jwt)
        if char == 'q':
            break

if __name__ == '__main__':
    menu()

