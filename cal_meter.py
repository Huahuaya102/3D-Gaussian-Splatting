from sklearn.linear_model import RANSACRegressor
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
from plyfile import PlyData
from sklearn.neighbors import LocalOutlierFactor

def read_ply_file(ply_path):
    """
    读取PLY文件并返回点云的坐标信息
    :param ply_path: PLY文件的路径
    :return: 点云的坐标数组
    """
    plydata = PlyData.read(ply_path)
    vertices = plydata['vertex']
    positions = np.vstack([vertices['x'], vertices['y'], vertices['z']]).T
    return positions

def fit_ground_plane(points):
    """
    拟合地面平面
    :param points: 点云的坐标数组
    :return: 地面平面的参数
    """
    X = points[:, :2]
    y = points[:, 2]
    poly = PolynomialFeatures(degree=1)
    X_poly = poly.fit_transform(X)
    ransac = RANSACRegressor()
    ransac.fit(X_poly, y)
    return ransac.estimator_.coef_, ransac.estimator_.intercept_

def project_points_to_plane(points, plane_coef, plane_intercept):
    """
    将点云数据投影到地面平面上
    :param points: 点云的坐标数组
    :param plane_coef: 地面平面的系数
    :param plane_intercept: 地面平面的截距
    :return: 投影后的点云坐标数组
    """
    X = points[:, :2]
    poly = PolynomialFeatures(degree=1)
    X_poly = poly.fit_transform(X)
    projected_z = np.dot(X_poly, plane_coef) + plane_intercept
    projected_points = np.column_stack((X, projected_z))
    return projected_points

def calculate_bounding_box(points):
    """
    计算点云的边界框
    :param points: 点云的坐标数组
    :return: 边界框的最小顶点和最大顶点
    """
    min_coords = np.min(points, axis=0)
    max_coords = np.max(points, axis=0)
    return min_coords, max_coords

def calculate_dimensions(min_coords, max_coords):
    """
    计算边界框的长、宽、高
    :param min_coords: 边界框的最小顶点
    :param max_coords: 边界框的最大顶点
    :return: 长、宽、高
    """
    length = max_coords[0] - min_coords[0]
    width = max_coords[1] - min_coords[1]
    height = max_coords[2] - min_coords[2]
    return length, width, height


ply_path = "/home/ubuntu/3d_cv_data_critical/gaussian_original_data/rgb-d_office_0321/pointcloud/1742525146092104/RGBDPoints_1742525146092104.ply" 
points = read_ply_file(ply_path)
plane_coef, plane_intercept = fit_ground_plane(points)
projected_points = project_points_to_plane(points, plane_coef, plane_intercept)
min_coords, max_coords = calculate_bounding_box(projected_points)
length, width, height = calculate_dimensions(min_coords, max_coords)

print(f"房间的长: {length}, 宽: {width}, 高: {height}")