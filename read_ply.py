from plyfile import PlyData

def print_ply_attributes(ply_file_path):
    try:
        # 读取 PLY 文件
        plydata = PlyData.read(ply_file_path)

        # 打印文件头信息
        print("文件头信息：")
        print(plydata.header)

        # 打印每个元素的属性
        for element in plydata.elements:
            print(f"\n元素名称: {element.name}")
            print("属性信息:")
            for property in element.properties:
                print(f"  - 属性名: {property.name}, 数据类型: {property.val_dtype}")

            # 打印元素的数量
            print(f"  元素数量: {len(element.data)}")

            # 检查是否为 vertex 元素（点云数据通常存储在这里）
            if element.name =='vertex':
                point_cloud_count = len(element.data)
                print(f"\n点云数量: {point_cloud_count}")

    except Exception as e:
        print(f"读取文件时出现错误: {e}")

# 使用示例
ply_file_path = '/home/ubuntu/3d_cv_data_critical/3dgs_server_output/20250424091521_output/point_cloud/iteration_60000/point_cloud.ply'
# ply_file_path = '/home/ubuntu/yjh/gaussian-splatting/data/office001/sparse/0/points3D.ply'
print_ply_attributes(ply_file_path)