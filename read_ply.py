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

    except Exception as e:
        print(f"读取文件时出现错误: {e}")

# 使用示例
ply_file_path = '/home/ubuntu/yjh/Scaffold-GS/outputs/test/baseline/2025-04-08_16:00:33/point_cloud/iteration_30000/point_cloud.ply'
# ply_file_path = '/home/ubuntu/yjh/gaussian-splatting/data/office001/sparse/0/points3D.ply'
print_ply_attributes(ply_file_path)