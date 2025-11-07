import json


# 安全解析json
def safe_json_parse(json_str: str) -> dict:
    start_idx = json_str.find('{')
    end_idx = json_str.rfind('}') + 1
    if start_idx != -1 and end_idx != 0:
        json_str = json_str[start_idx:end_idx]
        signal_data = json.loads(json_str)
    else:
        raise ValueError(f"无法解析JSON字符串")
    return signal_data
