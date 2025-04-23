import torch
import torch.nn as nn
import torch.optim as optim
import open3d as o3d
import numpy as np

# 定义自编码器网络
class PointCloudAutoencoder(nn.Module):
    def __init__(self):
        super(PointCloudAutoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(3, 64),
            nn.ReLU(),
            nn.Linear(64, 32)
        )
        self.decoder = nn.Sequential(
            nn.Linear(32, 64),
            nn.ReLU(),
            nn.Linear(64, 3)
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

# 加载点云数据
input_file_path = "/home/ubuntu/yjh/gaussian-splatting/output/office0410_depth/point_cloud/iteration_60000/point_cloud.ply"  # 原始点云文件路径
pcd = o3d.io.read_point_cloud(input_file_path)
points = np.asarray(pcd.points)
points_tensor = torch.tensor(points, dtype=torch.float32)

# 定义模型和优化器
model = PointCloudAutoencoder()
optimizer = optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.MSELoss()

# 训练自编码器
epochs = 100
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    output = model(points_tensor)
    loss = loss_fn(output, points_tensor)
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

# 计算重建误差并去除离群点
model.eval()
reconstructed_points = model(points_tensor).detach().numpy()
reconstruction_error = np.linalg.norm(points - reconstructed_points, axis=1)
threshold = np.percentile(reconstruction_error, 95)  # 设置阈值为95%的重建误差
outliers = reconstruction_error > threshold

# 去除离群点
filtered_points = points[~outliers]

# 创建新的点云对象
pcd_clean = o3d.geometry.PointCloud()
pcd_clean.points = o3d.utility.Vector3dVector(filtered_points)

# 显示去除离群点后的点云
o3d.visualization.draw_geometries([pcd_clean])

# 保存去除离群点后的点云到原文件格式
output_file_path = "/home/ubuntu/yjh/gaussian-splatting/output/office0410_depth/point_cloud/iteration_60000/output.ply" # 输出的点云文件路径
o3d.io.write_point_cloud(output_file_path, pcd_clean)

print(f"去除离群点后的点云已保存到: {output_file_path}")
