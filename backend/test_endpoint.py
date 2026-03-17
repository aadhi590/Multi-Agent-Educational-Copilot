import urllib.request
import urllib.error
import json

def test_chat():
    url = "http://127.0.0.1:8001/chat"
    payload = {
        "message": "Hello, I want to learn about Binary Search Tree.",
        "student_id": "test_student",
        "session_id": "test_session_123"
    }
    
    jsondata = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=jsondata)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    
    try:
        with urllib.request.urlopen(req) as response:
            res = response.read().decode('utf-8')
            with open("response.json", "w") as f:
                f.write(res)
            print("Success")
    except urllib.error.HTTPError as e:
        res = e.read().decode('utf-8')
        with open("error_response.json", "w") as f:
            f.write(res)
        print(f"Error {e.code}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_chat()
