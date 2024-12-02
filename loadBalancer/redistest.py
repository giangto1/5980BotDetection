import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.set("key", "whoaa")
value = r.get("key")
print(f"Value: {value}")
exists = r.exists("key")
print(f"Key exists: {bool(exists)}")
# r.delete("key")