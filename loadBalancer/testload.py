import requests


for i in range(10000):
    requests.get("http://localhost:5000/load/henry")
    print(i)