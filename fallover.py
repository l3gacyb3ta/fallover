from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
from tinydb import TinyDB, Query
import webbrowser, random

db = TinyDB('db.json', storage=CachingMiddleware(JSONStorage))

def search(keyword: str):
    keysearch = Query()
    res = db.search(keysearch.keywords.any(keyword))
    for i in res:
        print(i['url'])


def search_list(keyword: str):
    keysearch = Query()
    res = db.search(keysearch.keywords.any(keyword))
    key = []
    for i in res:
        key.append(i['url'])
    return key

go = True

helpmessage = """
Help:
search              - interactive search dialog, prints all found links
<any other word>    - opens a random link!
help                - print help
exit                - exits"""


print(helpmessage)

while go == True:
    com = input('> ').lower()

    if com == "search":
        search(input("key? "))
        continue
    
    if com == "help":
        print(helpmessage)
        continue
    
    if com == "exit":
        go = "NNOOOO GOOO"
        print("bye bye!")
        continue

    try:
        webbrowser.open(random.choice(search_list(com)))

    except IndexError:
        print("No entries")
    
