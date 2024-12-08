import json
import sys

def env_to_json(env_file, json_file):
    env_vars = {}
    
    with open(env_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    json_data = []
    for key, value in env_vars.items():
        json_data.append({
            "name": key,
            "value": value,
            "slotSetting": False
        })
    
    with open(json_file, 'w') as file:
        json.dump(json_data, file, indent=4)


if __name__ == "__main__":
    env_file = sys.argv[1]
    json_file = ".env.json"
    env_to_json(env_file, json_file)
