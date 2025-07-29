import pydualsense
import math


class DualSenseController(pydualsense.pydualsense):

    def __init__(self):
        super().__init__()
        self.init()

        # Joystick 初期化
        self.joystick_left_val = [0, 0]
        self.joystick_right_val = [0, 0]
        self.left_joystick_changed += self.on_joystick_left
        self.right_joystick_changed += self.on_joystick_right

        # Touchpad 累積位置と前回位置
        self.touch_position = [0.0, 0.0]
        self.prev_touch = None  # (x, y)

    # 左右ジョイスティックの正規化処理
    def on_joystick(self, stateX, stateY):
        stateX_norm = math.floor((stateX / 128) * 50) / 10
        stateY_norm = math.floor((stateY / 128) * 50) / 10
        self.is_joystick_in = not (-1 < stateX_norm < 1 and -1 < stateY_norm < 1)
        return [stateX_norm, stateY_norm]

    def on_joystick_left(self, stateX, stateY):
        self.joystick_left_val = self.on_joystick(stateX, stateY)

    def on_joystick_right(self, stateX, stateY):
        self.joystick_right_val = self.on_joystick(stateX, stateY)

    def get_joystick_left_val(self):
        return self.joystick_left_val

    def get_joystick_right_val(self):
        return self.joystick_right_val

    # --- タッチパッド処理 ---

    def apply_damped_diff(self, diff, alpha=0.01):
        return diff / (1 + alpha * abs(diff))

    def update_touchpad_position(self):
        t0 = self.state.trackPadTouch0
        t1 = self.state.trackPadTouch1

        if t0.isActive or t1.isActive:
            t = t0 if t0.isActive else t1
            x, y = t.X, t.Y

            if self.prev_touch is not None:
                dx = x - self.prev_touch[0]
                dy = y - self.prev_touch[1]

                damped_dx = self.apply_damped_diff(dx)
                damped_dy = self.apply_damped_diff(dy)

                self.touch_position[0] += damped_dx
                self.touch_position[1] += damped_dy

            self.prev_touch = (x, y)
        else:
            self.prev_touch = None  # タッチが離れたら初期化

    def get_touchpad_position(self):
        return self.touch_position



if __name__ == "__main__":
    dualsense = DualSenseController()
    try:
        while True: 
            dualsense.triggerR.setMode(pydualsense.TriggerModes.Rigid_A)
            dualsense.triggerR.setForce(1, 255)
    finally: 
        dualsense.close()
