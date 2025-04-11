import os
import shutil
from PIL import Image

# 定义可见光图和深度图文件夹路径
visible_folder = '/home/ubuntu/yjh/gaussian-splatting/data/test/images'
depth_folder = '/home/ubuntu/yjh/gaussian-splatting/data/test/depth_images'

# 获取两个文件夹中的文件列表，并按名称排序
visible_files = sorted(os.listdir(visible_folder))
depth_files = sorted(os.listdir(depth_folder))

# 检查两个文件夹中的文件数量是否一致
if len(visible_files) != len(depth_files):
    print("警告：可见光图和深度图的数量不一致！")
    min_length = min(len(visible_files), len(depth_files))
else:
    min_length = len(visible_files)

# 按顺序匹配文件并修改深度图文件名
for i in range(min_length):
    visible_file = visible_files[i]
    depth_file = depth_files[i]

    # 获取可见光图的文件名和扩展名
    visible_filename, visible_ext = os.path.splitext(visible_file)
    # 获取深度图的扩展名
    _, depth_ext = os.path.splitext(depth_file)

    # 构建新的深度图文件名
    new_depth_filename = visible_filename + depth_ext
    new_depth_file_path = os.path.join(depth_folder, new_depth_filename)
    old_depth_file_path = os.path.join(depth_folder, depth_file)

    try:
        # 修改深度图文件名
        shutil.move(old_depth_file_path, new_depth_file_path)
        print(f"匹配的可见光图: {visible_file}, 深度图从 {depth_file} 重命名为 {new_depth_filename}")
    except Exception as e:
        print(f"处理文件 {visible_file} 和 {depth_file} 时出错: {e}")