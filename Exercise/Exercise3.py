import time
from xarm.wrapper import XArmAPI
from DualSenseHID.DualSense import DualSenseController  # ← DualSense用クラス（別途実装）

"""
Exercise 3（DualSense版）:
この演習では、DualSenseコントローラの入力を使ってロボットアームを動かすコードを書いてください。
今回はロボットを正面から見て操作する前提で話を進めます。

ヒント：
- 左スティックでx軸・y軸方向に移動
- R1でz軸に+5mm（上）、L1でz軸に-5mm（下）
- ○ボタンを押したらグリッパー開閉（OperateGripper関数）
- PSボタンが押されたら終了

また、スピードや待機時間を変更して動きやすさを調整してみてください。
"""

################ 初期設定 ################

arm = XArmAPI("192.168.1.199")  # IP指定で接続
speed = 10

arm.set_mode(1)
arm.set_state(0)

arm.set_gripper_mode(0)
arm.set_gripper_enable(enable=True)
arm.set_gripper_speed(3000)

isGripperOpen = True
def OperateGripper():
    global isGripperOpen
    if isGripperOpen:
        arm.set_gripper_position(350, wait=True)
        isGripperOpen = False
    else:
        arm.set_gripper_position(800, wait=True)
        isGripperOpen = True

#########################################

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
    print("DualSense connected. 操作を開始してください。")
    try:
        while True:

            # ここにDualSenseの操作を実装
            # 左スティック（LX, LY） → x/y方向へ移動
            # R1 or L1 → z軸方向の移動
            # ○ボタン → グリッパー操作
            # PSボタン → breakで終了

            # ↓例：PSボタンが押されたら終了（実装時）
            # if dualsense.state.ps:
            #     print("Exiting...")
            #     break

            # 処理間隔
            time.sleep(0.05)
    finally:
        arm.disconnect()
        print("Disconnected from arm.") 
        dualsense.close()

if __name__ == "__main__":
    main()
    arm.disconnect()
