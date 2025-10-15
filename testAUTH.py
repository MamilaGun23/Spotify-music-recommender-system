# testAUTH.py
from Recommender.auth import get_spotify_client

def main():
    sp = get_spotify_client()
    user = sp.current_user()  # fetch profile info
    print("✅ Authentication successful!")
    if user is not None:
        print(f"Logged in as: {user['display_name']} (id: {user['id']})")
    else:
        print("Failed to fetch user profile information.")

if __name__ == "__main__":
    main()

