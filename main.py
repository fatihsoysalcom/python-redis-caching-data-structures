import redis
import time
import json # To store structured data in Redis as a string

# --- Redis Connection ---
# Assumes Redis server is running on localhost:6379
# You can change these if your Redis instance is elsewhere.
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping() # Test connection
    print("Successfully connected to Redis!")
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")
    print("Please ensure a Redis server is running on localhost:6379.")
    exit(1)

# --- Simulate a slow database call ---
def get_data_from_database(item_id):
    """
    Simulates fetching data from a slow database.
    """
    print(f"Fetching item '{item_id}' from database...")
    time.sleep(2) # Simulate network latency or complex query
    data = {
        "id": item_id,
        "name": f"Product {item_id}",
        "description": f"This is a detailed description for product {item_id}.",
        "price": round(float(item_id) * 10.5, 2)
    }
    print(f"Data for '{item_id}' retrieved from database.")
    return data

# --- Caching Logic with Redis ---
def get_cached_item(item_id, cache_ttl=30):
    """
    Retrieves an item, first checking Redis cache.
    If not found, fetches from the database and caches it.
    """
    cache_key = f"product:{item_id}" # Define a clear cache key

    # Try to get data from Redis
    cached_data_str = r.get(cache_key) # Redis stores strings

    if cached_data_str:
        # Cache hit! Redis's in-memory nature provides lightning-fast access.
        print(f"Cache HIT for key: {cache_key}")
        return json.loads(cached_data_str) # Deserialize JSON string back to dict
    else:
        # Cache miss! Fetch from database
        print(f"Cache MISS for key: {cache_key}. Fetching from database...")
        data = get_data_from_database(item_id)

        # Store data in Redis with an expiration time (TTL)
        # This is a core Redis caching strategy to reduce database load.
        r.setex(cache_key, cache_ttl, json.dumps(data)) # Serialize dict to JSON string
        print(f"Data for '{item_id}' cached in Redis with TTL: {cache_ttl} seconds.")
        return data

# --- Demonstrate Redis's versatile data structures (Hash) ---
def manage_user_profile(user_id, username, email):
    """
    Demonstrates using Redis Hashes to store structured user profile data.
    Hashes are ideal for representing objects with multiple fields.
    """
    user_key = f"user:{user_id}"
    print(f"\nManaging user profile for {user_id} using Redis Hash...")

    # Set multiple fields in a hash
    # Redis Hashes allow storing multiple key-value pairs under a single key,
    # making them efficient for object storage beyond simple key-value.
    r.hset(user_key, mapping={
        "username": username,
        "email": email,
        "last_login": time.time()
    })
    print(f"User '{username}' profile updated in Redis Hash: {user_key}")

    # Retrieve all fields from the hash
    profile = r.hgetall(user_key)
    print(f"Retrieved user profile for {user_id}: {profile}")
    return profile

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Demonstrating Redis Caching ---")

    # First call - cache miss, data fetched from 'database'
    item_1_data = get_cached_item("101")
    print(f"Retrieved item 101: {item_1_data}\n")

    # Second call for the same item - cache hit, data from Redis (should be fast)
    item_1_data_cached = get_cached_item("101")
    print(f"Retrieved item 101 (cached): {item_1_data_cached}\n")

    # Call for a different item - cache miss
    item_2_data = get_cached_item("202")
    print(f"Retrieved item 202: {item_2_data}\n")

    print("--- Demonstrating Redis Hashes ---")
    manage_user_profile("user:1", "alice", "alice@example.com")
    manage_user_profile("user:2", "bob", "bob@example.com")

    # Clean up (optional) - uncomment to remove keys after run
    # r.delete("product:101", "product:202", "user:1", "user:2")
    # print("\nCleaned up example keys from Redis.")

    print("\nRedis example finished.")
