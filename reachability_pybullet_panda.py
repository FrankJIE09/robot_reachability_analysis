import pybullet as p
import numpy as np
import trimesh
import pybullet_data
import random

# 设置PyBullet仿真环境
p.connect(p.GUI)  # 使用GUI连接来显示机械臂的3D模型
p.setAdditionalSearchPath(pybullet_data.getDataPath())  # 设置URDF文件的搜索路径

# 加载Franka Panda机械臂的URDF文件
robot_id = p.loadURDF("./franka_panda/panda.urdf", useFixedBase=True)

# 获取机械臂关节信息
num_joints = p.getNumJoints(robot_id)
joint_ranges = []
for joint_index in range(num_joints):
    joint_info = p.getJointInfo(robot_id, joint_index)
    # 检查关节是否为可运动关节 (即非固定关节)
    if joint_info[2] == p.JOINT_REVOLUTE:  # 只记录旋转关节
        joint_ranges.append((joint_info[8], joint_info[9]))  # 关节的最小值和最大值

# 采样数量
num_samples = 10000
reachability_points = []

# 随机采样关节空间，计算末端执行器的位置
for _ in range(num_samples):
    joint_positions = []
    for min_val, max_val in joint_ranges:
        joint_positions.append(random.uniform(min_val, max_val))

    # 设置关节位置
    p.setJointMotorControlArray(
        bodyIndex=robot_id,
        jointIndices=list(range(len(joint_ranges))),
        controlMode=p.POSITION_CONTROL,
        targetPositions=joint_positions,
    )
    p.stepSimulation()

    # 获取末端执行器的位置
    end_effector_state = p.getLinkState(robot_id, num_joints - 1)  # 或指定末端执行器的链接索引
    position = end_effector_state[4]  # 位置(x, y, z)
    reachability_points.append(position)

# 转换为NumPy数组
reachability_points = np.array(reachability_points)

# 创建可达空间的点云
reachability_cloud = trimesh.points.PointCloud(reachability_points, colors=[0, 0, 255, 100])  # 半透明的蓝色可达空间

# 创建场景并添加可达空间
scene = trimesh.Scene()
scene.add_geometry(reachability_cloud)
scene.show()  # 在新的窗口中显示可达空间的3D点云

# PyBullet的窗口显示Franka Panda机械臂3D模型
# 用户可以在PyBullet的GUI中交互式观察机械臂

# 注意: 使用 p.disconnect() 仅在你关闭展示窗口时
