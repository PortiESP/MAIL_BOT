import requests, json



def printJSON(data, ntabs=1):
    tabs = '\t'*ntabs
    for key, value in data.items():
        if not isinstance(value, dict):
            print(f"{tabs}{key}: {value}")
        else:
            printJSON(value, ntabs+1)





if __name__ == '__main__':
    url = "https://api.mail.tm"
    endpoint = "accounts"

    reqheaders = {"accept": "application/ld+json", "Content-Type": "application/json"}
    data = {"address": "pepdsadasdfde@knowledgemd.com", "password": "test1"}

    res = requests.post(f"{url}/{endpoint}", json=data, headers=reqheaders)

    soup = Soup(res.content)
    print(soup)
    printJSON(res.json())




