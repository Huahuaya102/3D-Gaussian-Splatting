import requests
import time

# 发起 POST 请求启动建模任务
url = "http://192.168.100.117:5000/run_bash_script"
# 图像路径数组

data = {
    "pic_dir_name": 'test'
}
response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    task_id = result.get("task_id")
    print(f"Task ID: {task_id}")
    print("3D reconstruction started")
else:
    print("Error:", response.json())

# 定期查询任务状态
while True:
    # task_id = "20250424154143"
    url = f"http://192.168.100.117:5000/check_service_status?task_id={task_id}"
    response = requests.get(url)

    if response.status_code == 200:
        result = response.json()
        status = result.get("status")
        task_completed = result.get('task_completed')
        print(f"Task Status: {result.get('message')}")
        print(f"status: {status}")
        print(f"task_completed: {task_completed}")

        if not status.get('process_running'):
            break
    else:
        print("Error:", response.json())

    time.sleep(5)  # 每 5 秒查询一次