
import requests

def main():
    print("🚀 Testing Admin Schema Refresh...")
    try:
        url = "http://localhost:8000/api/v1/admin/refresh-schema"
        print(f"POST {url}")
        
        response = requests.post(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Schema refresh successful!")
        else:
            print("❌ Failed to refresh schema.")
            
    except Exception as e:
        print(f"❌ Connection failed (is server running?): {e}")

if __name__ == "__main__":
    main()
