import requests
import os

url = 'http://localhost:8000/api/upload/'
auth = ('admin', 'admin123')
file_path = 'sample_equipment_data.csv'

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    exit(1)

files = {'file': open(file_path, 'rb')}

try:
    response = requests.post(url, files=files, auth=auth)
    print(f"Status Code: {response.status_code}")
    print("Response Body:", response.text)
    
    if response.status_code == 201:
        print("\n✅ SUCCESS: File uploaded successfully with Basic Auth.")
    else:
        print("\n❌ FAILURE: Upload failed.")
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
