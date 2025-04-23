from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import subprocess
import threading
import time
import json
import psutil


app = Flask(__name__)
# 允许所有域名进行跨域请求
CORS(app)

# 图像数据根目录
FILE_PATH = "/home/ubuntu/3d_cv_data_critical/3dgs_server_data/" 
# 历史任务存储文件路径
TASK_HISTORY_FILE = "/home/ubuntu/3d_cv_data_critical/3dgs_server_output/task_history.json"
# 存储当前运行的三维重建任务的字典
running_tasks = {}

# 将任务信息保存到历史任务文件中
def save_task_to_history(task_id, status, pid, log_file, model_path="", has_error=False):
    task_data = {
        "task_id": task_id,
        "status": status,
        "pid": pid,
        "log_file": log_file,
        "model_path": model_path,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "has_error": has_error
    }

    # 如果历史文件存在，加载历史任务
    if os.path.exists(TASK_HISTORY_FILE):
        with open(TASK_HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []

    # 添加新任务到历史记录
    history.append(task_data)

    # 保存历史任务信息
    with open(TASK_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)


# 三维重建
def run_3d_reconstruction(task_id, path, log_file):
    script_path = '/home/ubuntu/yjh/3DGSPipeline.sh'
    command = [script_path] + [path]

    try:
        with open(log_file, 'w', encoding='utf-8') as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, text=True)
            running_tasks[task_id] = {'pid': process.pid, 'log_file': log_file, 'status': 'running'}
            process.wait()
            time.sleep(2) # 确保日志文件写入完成

            # 读取日志文件，提取model_path
            model_path = ""
            has_error = False
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    if 'error' in log_content.lower():
                        has_error = True
                    # 提取model_path
                    for line in log_content.splitlines():
                        if 'model_path:' in line:
                            model_path = line.split('model_path:')[1].strip()
                            break
            
            # 如果日志没有包含model_path，则从日志中寻找"3DGS Reconstruction completed!"来确保任务完成
            if not model_path:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    if '3DGS Reconstruction completed!' in log_content:
                        # 强制更新状态为completed
                        running_tasks[task_id]['status'] = 'completed'
                        model_path = "Not Found"
                    else:
                        running_tasks[task_id]['status'] = 'failed'
                        save_task_to_history(task_id, 'failed', process.pid, log_file, "", has_error)
                        return
            
            final_status = 'completed' if not has_error else 'failed'
            running_tasks[task_id]['status'] = final_status
            save_task_to_history(task_id, final_status, process.pid, log_file, model_path, has_error)

    except Exception as e:
        running_tasks[task_id]['status'] = 'failed'
        save_task_to_history(task_id, 'failed', process.pid, log_file, "", True)

@app.route('/run_bash_script', methods=['POST'])
def run_bash_script():
    data = request.get_json()
    path = data.get('pic_dir_name')

    if not path or not isinstance(path, str):
        return jsonify({'message': 'Invalid paths. Expected an array of paths.', 'state': 'falure'}), 400

    file_list = os.listdir(FILE_PATH)
    if path not in file_list:
        return jsonify({'message': 'The path does not exist.', 'state': 'failure'}), 404
    

    try:
        # 生成一个唯一的任务ID
        task_id = datetime.now().strftime("%Y%m%d%H%M%S")
        # 定义日志文件的路径
        log_file_name = f"{task_id}_script_log.txt"
        log_file = os.path.join(app.root_path, log_file_name)

        # 在新线程中启动三维重建进程
        thread = threading.Thread(target=run_3d_reconstruction, args=(task_id, path, log_file))
        thread.start()
        
        # 立即返回任务ID
        return jsonify({
            'message': '3D Reconstruction Started', 
            'state': 'success',
            'task_id': task_id,
        }), 200
    
    except Exception as e:
        return jsonify({
            'message': f'3D Reconstruction failed: {str(e)}',
            'state': 'failure'
        }), 500
    

@app.route('/check_service_status', methods=['GET'])
def check_service_status():
    try:
        task_id = request.args.get('task_id')
        if not task_id:
            return jsonify({'message': 'Task ID is required', 'state': 'failure'}), 400
        
        # 增加等待时间，确保任务稳定运行
        time.sleep(5)

        process_running = False
        log_error = False
        model_path = ""
        task_completed = False

        # 检查当前任务是否正在运行
        if task_id in running_tasks:
            task_status = running_tasks[task_id]['status']
            if task_status == 'running':
                try:
                    process = psutil.Process(running_tasks[task_id]['pid'])
                    process_running = process.is_running()
                    # 检查子进程是否仍在运行
                    for child in process.children(recursive=True):
                        if child.is_running():
                            process_running = True
                            break
                except psutil.NoSuchProcess:
                    import logging
                    logging.error(f"Process with PID {running_tasks[task_id]['pid']} not found.")
                    process_running = False
            elif task_status == 'completed':
                process_running = False
                task_completed = True
                log_file = running_tasks[task_id]['log_file']
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                        if 'error' in log_content.lower():
                            log_error = True
                            task_completed = False
                            running_tasks[task_id]['status'] = 'failed'
                            save_task_to_history(task_id, 'failed', running_tasks[task_id]['pid'], log_file, "")
                        else:
                            task_completed = True
            
        # 如果当前任务没有找到，查询历史任务
        if not process_running:
            # 读取历史任务文件
            if os.path.exists(TASK_HISTORY_FILE):
                with open(TASK_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    for task in history:
                        if task['task_id'] == task_id:
                            task_status = task['status']
                            task_completed = task_status == 'completed'
                            log_error = task['has_error']
                            log_file = task['log_file']
                            model_path = task.get('model_path', '')
                            break
            
        status = {
            'process_running': process_running,
            'log_error': log_error,
            'model_path': model_path if process_running or task_completed else "",
            'task_completed': task_completed
        }

        if (process_running or task_completed) and not log_error:
            message = '3DGS Reconstruction completed' if task_completed else 'Service is running normally'
            state = 'success' if task_completed else 'building'
        else:
            message = 'Service may have issues'
            state = 'failure'

        return jsonify({
            'message': message,
            'state': state,
            'status': status,
            'task_id': task_id,
            'task_completed': task_completed
        }), 200
    
    except Exception as e:
        return jsonify({
            'message': f'Service status check failed: {str(e)}',
            'state': 'failure'
        }), 500
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)       