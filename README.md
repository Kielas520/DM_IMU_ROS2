# dm_imu

达妙 (DaMiao) IMU 的 ROS 2 驱动节点。
本节点通过串口与达妙 IMU 进行通信，以非阻塞后台线程的方式实时读取并解析串口协议帧（包含完整的 CRC16 校验），并将其转换为标准的 ROS 2 消息格式进行发布。

## 1. 特性

* **多话题输出**：
  * `/imu/data` (`sensor_msgs/msg/Imu`): 包含转换后的四元数姿态信息。
  * `/imu/rpy` (`geometry_msgs/msg/Vector3Stamped`): 直观的欧拉角输出（Roll, Pitch, Yaw）。
  * `/imu/pose` (`geometry_msgs/msg/PoseStamped`): 包含姿态的位姿信息，原点固定，方便直接在 RViz 中进行可视化。
* **高频与高可靠性**：
  * 底层串口采用后台独立线程读取，保证数据缓存及时清空。
  * 主节点以 200 Hz 的频率进行无阻塞轮询与发布。
  * 包含完整的数据帧校验（头部校验及 CCITT CRC16 校验），支持自动适应是否包含帧头的 CRC 模式。
* **灵活配置**：
  * 支持自定义串口号、波特率、坐标系名称。
  * 可配置 QoS 策略（Reliable 或 BestEffort），兼容不同的网络状态或 RViz 显示需求。

## 2. 环境依赖

* **操作系统**: Ubuntu 22.04 (推荐)
* **ROS 2 版本**: Humble
* **Python 依赖**: `pyserial`

安装 `pyserial`：
```bash
sudo apt update
sudo apt install python3-serial
# 或者使用 pip：pip3 install pyserial
```

## 3. 安装与编译

将本仓库克隆到你的 ROS 2 工作空间的 `src` 目录下，然后进行编译：

```bash
cd ~/ros2_ws/src
# 克隆代码仓库 (替换为实际的仓库地址)
git clone <repository_url> dm_imu

cd ~/ros2_ws
# 解决依赖
rosdep install --from-paths src --ignore-src -r -y

# 编译
colcon build --packages-select dm_imu

# 刷新环境变量
source install/setup.bash
```

## 4. 权限配置 (重要)

如果设备挂载为 `/dev/ttyACM0` 或 `/dev/ttyUSB0`，在运行节点前需要确保当前用户具有串口访问权限。可以通过以下命令将当前用户加入 `dialout` 用户组：

```bash
sudo usermod -aG dialout $USER
```
*注：执行完成后需要注销并重新登录终端，或者重启电脑才能生效。*

也可以使用 `udev` 规则永久赋予权限：
```bash
sudo bash -c 'echo "KERNEL==\"ttyACM*\", MODE=\"0666\"" > /etc/udev/rules.d/99-dm-imu.rules'
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## 5. 参数配置

配置文件路径：`config/params.yaml`

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `port` | string | `"/dev/ttyACM0"` | IMU 设备串口节点路径 |
| `baudrate` | int | `921600` | 串口波特率 |
| `frame_id` | string | `"imu_link"` | 发布消息的坐标系 ID |
| `publish_rpy` | bool | `true` | 是否额外发布 `/imu/rpy` 欧拉角话题 |
| `qos_reliable`| bool | `true` | `true` 为 Reliable (历史深度 50)；`false` 为 BestEffort (Sensor Data 策略) |
| `verbose` | bool | `true` | 是否在终端输出实时的 RPY 打印信息及统计警告 |

*修改提示：如果 RViz2 无法接收到话题，通常是因为 QoS 不匹配，请检查 RViz 中的 Reliability 设置是否与 `qos_reliable` 参数一致。*

## 6. 发布的话题

* **`/imu/data`** (`sensor_msgs/msg/Imu`)
  核心话题，包含 IMU 姿态（四元数格式）。当前固件暂未配置线加速度与角速度的协方差（对应协方差矩阵元素设为 -1.0）。
* **`/imu/rpy`** (`geometry_msgs/msg/Vector3Stamped`)
  欧拉角输出。默认单位为**弧度(rad)**。若需要修改为度(deg)，可直接在 `node.py` 中将 `self.publish_rpy_in_degree` 设为 `True`。
* **`/imu/pose`** (`geometry_msgs/msg/PoseStamped`)
  位姿话题，位置固定为 `(0,0,0)`，姿态与 IMU 实时同步，非常适合通过 RViz 的 `Pose` 插件快速观察传感器朝向。

## 7. 运行节点

可以通过基础的 ros2 run 命令直接运行节点：

```bash
ros2 run dm_imu dm_imu_node --ros-args --params-file src/dm_imu/config/params.yaml
```

**使用 Launch 文件运行 (推荐)：**
本包内附带了 launch 启动脚本，支持带参数启动并加载配置。

1. 仅启动 IMU 节点：
```bash
ros2 launch dm_imu dm_imu.launch.py
```

2. 启动 IMU 节点并同时打开 RViz 可视化：
```bash
ros2 launch dm_imu dm_imu_rviz.launch.py
```

## 8. 常见问题排查

1. **终端不断提示 "No frames yet from serial (≈1s)"**
   - 检查串口物理连接是否松动。
   - 检查设备的波特率设置是否确实为 921600。
   - 确认串口权限已正确配置。
2. **"Unknown latest frame format"**
   - 串口解析出错了，或者 IMU 的固件协议版本与 `dm_serial.py` 中的解析格式（`[0,1]=0x55,0xAA` 等）不一致。
3. **RViz 提示 Global Status: Warn (No tf data)**
   - 在 RViz的 "Global Options" -> "Fixed Frame" 中手动输入你在 `params.yaml` 配置的 `frame_id`（默认是 `imu_link`）。
