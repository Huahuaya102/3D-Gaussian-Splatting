import os
from PIL import Image
import pillow_heif

# 注册HEIF文件类型
pillow_heif.register_heif_opener()

def heic_to_png(heic_path, output_dir):
    """
    将HEIC图像转换为PNG图像
    :param heic_path: HEIC图像的路径
    :param output_dir: 输出PNG图像的目录
    """
    try:
        # 打开HEIC图像
        image = Image.open(heic_path)
        # 获取文件名（不包含扩展名）
        file_name = os.path.splitext(os.path.basename(heic_path))[0]
        # 构建输出PNG图像的路径
        output_path = os.path.join(output_dir, f"{file_name}.png")
        # 保存为PNG图像
        image.save(output_path, "PNG")
        print(f"成功将 {heic_path} 转换为 {output_path}")
    except Exception as e:
        print(f"转换 {heic_path} 时出现错误: {e}")

def convert_all_heic_in_dir(input_dir, output_dir):
    """
    转换指定目录下的所有HEIC图像为PNG图像
    :param input_dir: 输入HEIC图像的目录
    :param output_dir: 输出PNG图像的目录
    """
    # 如果输出目录不存在，则创建它
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # 遍历输入目录中的所有文件
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.heic'):
                heic_path = os.path.join(root, file)
                heic_to_png(heic_path, output_dir)

if __name__ == "__main__":
    # 输入HEIC图像的目录
    input_directory = "/home/ubuntu/3d_cv_data_critical/gaussian_original_data/office0411/input"
    # 输出PNG图像的目录
    output_directory = "/home/ubuntu/3d_cv_data_critical/gaussian_original_data/office0411/output"
    convert_all_heic_in_dir(input_directory, output_directory)