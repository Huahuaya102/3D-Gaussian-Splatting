import requests

# 定义请求的 URL
url = 'http://192.168.100.117:5000/run_bash_script'

# 定义要发送的数据
data = {
    'pic_dir_name': 'test'
}

try:
    # 发起 POST 请求
    response = requests.post(url, json=data)

    # 检查响应状态码
    if response.status_code == 200:
        # 打印响应内容
        print(response.json())
    else:
        print(f"请求失败，状态码: {response.status_code}")
except requests.RequestException as e:
    print(f"请求发生错误: {e}")    