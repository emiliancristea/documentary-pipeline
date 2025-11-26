import json
import os
import numpy as np

def test_json():
    path = "models/kokoro/voices.json"
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        print("Success: Loaded JSON.")
        keys = list(data.keys())
        print(f"Keys: {keys[:5]}...")
        
        # Check if 'af_sky' is there
        if 'af_sky' in data:
            print("af_sky found.")
            arr = np.array(data['af_sky'])
            print(f"Shape: {arr.shape}")
        else:
            print("af_sky NOT found.")
            
    except Exception as e:
        print(f"Failed to load JSON: {e}")

if __name__ == "__main__":
    test_json()
