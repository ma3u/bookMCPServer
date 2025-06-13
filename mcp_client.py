import requests
import json

SERVER_URL = "http://localhost:8000/mcp"  # Adjust if your server runs on a different port/path

QUERY_PAYLOAD = {
    "name": "query",
    "input": {
        "query": "Vitamin D Mangel",
        "top_k": 5
    },
    "id": "q1"
}

def send_query():
    """Sends the predefined query to the MCP server and prints the response."""
    headers = {
        "Content-Type": "application/json"
    }
    try:
        print(f"Sending query to {SERVER_URL}...")
        print(f"Payload: {json.dumps(QUERY_PAYLOAD, indent=2)}\n")
        
        response = requests.post(SERVER_URL, json=QUERY_PAYLOAD, headers=headers)
        
        print(f"Response Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print("Response JSON:")
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print("Could not decode JSON response.")
                print(f"Response Text: {response.text}")
        else:
            print(f"Error: Server returned status code {response.status_code}")
            print(f"Response Text: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: Could not connect to the server at {SERVER_URL}.")
        print("Please ensure the MCP server is running and accessible.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    send_query()
