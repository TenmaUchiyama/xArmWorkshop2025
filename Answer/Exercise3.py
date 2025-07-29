import time
from xarm.wrapper import XArmAPI
from DualSense import DualSenseController  

################ 初期設定 ################

arm = XArmAPI("192.168.1.199")
speed = 10
def init():
    print("Initializing arm...")

    arm.clean_error()
    arm.clean_warn()

    # サーボ有効化（この戻り値をチェック）
    code = arm.motion_enable(enable=True)
    if code != 0:
        print(f"[ERROR] motion_enable failed, code={code}")
    else:
        print("motion_enable success")

    arm.set_mode(1)
    arm.set_state(0)

    # 状態確認
    state = arm.get_state()
    print("Arm state:", state)

    # グリッパー
    arm.set_gripper_mode(0) 
    arm.set_gripper_enable(enable=True)
    arm.set_gripper_speed(3000)

init()
               

isGripperOpen = True
def OperateGripper():
    global isGripperOpen
    if isGripperOpen:
        arm.set_gripper_position(350, wait=True)
        isGripperOpen = False
    else:
        arm.set_gripper_position(800, wait=True)
        isGripperOpen = True

def CheckIfNewPositionInWorkspace(x, y, z):
    if x > 680 or x < 300:
        return False
    if y < -230 or y > 420:
        return False
    if z < 94 or z > 550:
        return False
    return True

def SetPosition(x, y, z, roll, pitch, yaw):
    if CheckIfNewPositionInWorkspace(x, y, z):
        _, target_angle = arm.get_inverse_kinematics([x, y, z, roll, pitch, yaw])
        arm.set_servo_angle_j(angles=target_angle, speed=speed)
    else:
        print("position is out of workspace")

#########################################

def main():
    dualsense = DualSenseController()
    print("DualSense ready. Use L-stick for XY, R1/L1 for Z, ○ to grip, PS to exit.")

    try:
        while not dualsense.state.ps:
            # 入力取得
            lx, ly = dualsense.get_joystick_left_val()  # [x, y] = 左スティック
            z_dir = 0
            if dualsense.state.R1:
                z_dir += 5  # 上昇
            if dualsense.state.L1:
                z_dir -= 5  # 下降

            # 現在位置取得
            _, position = arm.get_position()
            x, y, z, roll, pitch, yaw = position

            # 方向ベクトルから座標更新（XYは逆に感じるなら±切り替え可能）
            SetPosition(
                x + ly * 1.5,     # 左スティック上下 → x方向
                y + lx * 1.5,     # 左スティック左右 → y方向
                z + z_dir,      # ボタン → z方向
                roll, pitch, yaw
            )

            # ○ボタンでグリッパー操作
            if dualsense.state.circle:
                OperateGripper()
                while dualsense.state.circle:
                    time.sleep(0.1)  # 連続実行防止

            time.sleep(0.05)

    finally:
        
        arm.disconnect()
        dualsense.close()
        print("Disconnected.")

if __name__ == "__main__":
    main()
