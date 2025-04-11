# from plyfile import PlyData, PlyElement
# import numpy as np
# import open3d as o3d

# def convert_ply_ascii_to_binary(input_file, output_file):
#     # 读取 ASCII 格式的 PLY 文件
#     plydata = PlyData.read(input_file)

#     # 获取顶点数据
#     vertices = plydata['vertex']

#     # 提取坐标和颜色数据
#     x = vertices['x']
#     y = vertices['y']
#     z = vertices['z']
#     red = vertices['red']
#     green = vertices['green']
#     blue = vertices['blue']

#     # 假设法向量默认值为 (0, 0, 0)
#     num_vertices = len(vertices)
#     nx = np.zeros(num_vertices, dtype=np.float32)
#     ny = np.zeros(num_vertices, dtype=np.float32)
#     nz = np.zeros(num_vertices, dtype=np.float32)

#     # 创建新的顶点数据数组
#     new_vertex_data = np.empty(num_vertices, dtype=[
#         ('x', 'f4'), ('y', 'f4'), ('z', 'f4'),
#         ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4'),
#         ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')
#     ])

#     # 填充新的顶点数据
#     new_vertex_data['x'] = x
#     new_vertex_data['y'] = y
#     new_vertex_data['z'] = z
#     new_vertex_data['nx'] = nx
#     new_vertex_data['ny'] = ny
#     new_vertex_data['nz'] = nz
#     new_vertex_data['red'] = red
#     new_vertex_data['green'] = green
#     new_vertex_data['blue'] = blue

#     # 创建新的 PLY 元素
#     new_vertex_element = PlyElement.describe(new_vertex_data, 'vertex')

#     # 创建新的 PLY 数据
#     new_plydata = PlyData([new_vertex_element], text=False)

#     # 保存为二进制小端格式的 PLY 文件
#     new_plydata.write(output_file)

# def downsample_ply_file(input_file, output_file, voxel_size=0.01):
#     # 读取 PLY 文件
#     pcd = o3d.io.read_point_cloud(input_file)

#     # 进行体素降采样
#     downsampled_pcd = pcd.voxel_down_sample(voxel_size=voxel_size)

#     # 保存降采样后的点云
#     o3d.io.write_point_cloud(output_file, downsampled_pcd)


# if __name__ == '__main__':
#     # 使用示例
#     input_file = '/home/ubuntu/yjh/gaussian-splatting/data/test/sparse/0/points3D.ply'
#     output_file = '/home/ubuntu/yjh/gaussian-splatting/data/test/sparse/0/points3D.ply'
#     downsample_file = '/home/ubuntu/yjh/gaussian-splatting/data/test/sparse/0/downsample.ply'
#     # convert_ply_ascii_to_binary(input_file, output_file)
#     downsample_ply_file(output_file, downsample_file , voxel_size=0.01)




import numpy as np
from plyfile import PlyData, PlyElement
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA

def estimate_normals(points, k=10):
    """
    估算点云的法向量
    :param points: 点云数据，形状为 (N, 3)
    :param k: 近邻数量
    :return: 法向量，形状为 (N, 3)
    """
    num_points = points.shape[0]
    normals = np.zeros((num_points, 3))

    # 使用最近邻搜索找到每个点的k近邻
    nbrs = NearestNeighbors(n_neighbors=k, algorithm='ball_tree').fit(points)
    distances, indices = nbrs.kneighbors(points)

    for i in range(num_points):
        # 获取当前点的k近邻
        neighbors = points[indices[i]]

        # 使用PCA估算法向量
        pca = PCA(n_components=3)
        pca.fit(neighbors)
        normal = pca.components_[-1]

        normals[i] = normal

    return normals

def add_normals_to_ply(ply_path):
    """
    读取PLY文件，估算点云的法向量，并将法向量写回到PLY文件中
    :param ply_path: PLY文件的路径
    """
    # 读取PLY文件
    plydata = PlyData.read(ply_path)
    vertices = plydata['vertex']
    points = np.vstack([vertices['x'], vertices['y'], vertices['z']]).T

    # 估算点云的法向量
    normals = estimate_normals(points)

    # 将法向量添加到PLY文件中
    vertex_data = []
    for i in range(len(vertices)):
        vertex = (
            vertices['x'][i],
            vertices['y'][i],
            vertices['z'][i],
            vertices['red'][i],
            vertices['green'][i],
            vertices['blue'][i],
            normals[i][0],
            normals[i][1],
            normals[i][2]
        )
        vertex_data.append(vertex)

    # 定义新的PLY元素
    vertex_dtype = [
        ('x', 'f4'),
        ('y', 'f4'),
        ('z', 'f4'),
        ('red', 'u1'),
        ('green', 'u1'),
        ('blue', 'u1'),
        ('nx', 'f4'),
        ('ny', 'f4'),
        ('nz', 'f4')
    ]
    vertex_element = PlyElement.describe(np.array(vertex_data, dtype=vertex_dtype), 'vertex')

    # 创建新的PLY数据
    new_plydata = PlyData([vertex_element])

    # 保存新的PLY文件
    new_ply_path = ply_path.replace('.ply', '_with_normals.ply')
    new_plydata.write(new_ply_path)
    print(f"添加法向量后的PLY文件已保存到: {new_ply_path}")

def convert_ply_format(input_path, output_path):
    # 读取原始的 .ply 文件
    plydata = PlyData.read(input_path)
    vertices = plydata['vertex']

    # 提取属性
    x = vertices['x']
    y = vertices['y']
    z = vertices['z']
    red = vertices['red']
    green = vertices['green']
    blue = vertices['blue']
    nx = vertices['nx']
    ny = vertices['ny']
    nz = vertices['nz']

    # 定义新的属性顺序
    dtype = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'),
             ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4'),
             ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')]

    # 创建新的结构化数组
    elements = np.empty(len(vertices), dtype=dtype)
    elements['x'] = x
    elements['y'] = y
    elements['z'] = z
    elements['nx'] = nx
    elements['ny'] = ny
    elements['nz'] = nz
    elements['red'] = red
    elements['green'] = green
    elements['blue'] = blue

    # 创建新的 PlyElement 对象
    vertex_element = PlyElement.describe(elements, 'vertex')

    # 创建新的 PlyData 对象并写入文件
    new_ply_data = PlyData([vertex_element])
    new_ply_data.write(output_path)

if __name__ == '__main__':
    ply_path = '/home/ubuntu/yjh/gaussian-splatting/data/test/sparse/0/points3D_with_normals.ply'
    output_path = '/home/ubuntu/yjh/gaussian-splatting/data/test/sparse/0/points3D_end.ply'
    convert_ply_format(ply_path, output_path)
    # add_normals_to_ply(ply_path)