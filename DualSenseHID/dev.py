import time
import pydualsense
import math

ds = pydualsense.pydualsense()
ds.init()

# 現在の「見かけ上の位置」
pos_x, pos_y = 0.0, 0.0
prev_x, prev_y = None, None  # Noneで最初だけ無視

def apply_damped_diff(diff, alpha=0.01):
    return diff / (1 + alpha * abs(diff))  # 差が大きいと抑えが強くなる

try:
    while True:
        t0 = ds.state.trackPadTouch0
        t1 = ds.state.trackPadTouch1

        if t0.isActive or t1.isActive:
            t = t0 if t0.isActive else t1
            x, y = t.X, t.Y

            if prev_x is not None:
                dx = x - prev_x
                dy = y - prev_y

                damped_dx = apply_damped_diff(dx)
                damped_dy = apply_damped_diff(dy)

                pos_x += damped_dx
                pos_y += damped_dy

                print(f"pos_x: {pos_x:.2f}, pos_y: {pos_y:.2f}  (Δx: {dx}, Δy: {dy})")

            prev_x, prev_y = x, y

        else:
            # タッチが離されたら次回の差分をスキップするように
            prev_x, prev_y = None, None

        time.sleep(0.016)  # 約60fps

except KeyboardInterrupt:
    print("Exit requested.")
finally:
    ds.close()
