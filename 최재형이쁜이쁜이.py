"""유령정체 미니 시뮬레이션 (Nagel-Schreckenberg)
조작: 화면 아래 버튼만 사용 (밀도 −/+, 감속확률 −/+, 속도 −/+, 급브레이크, 일시정지, 초기화)
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from matplotlib.colors import LinearSegmentedColormap

plt.rcParams["font.family"] = ["Malgun Gothic", "AppleGothic", "NanumGothic", "DejaVu Sans"]

L, VMAX = 200, 5                                   # 도로 길이(칸), 최고속도
S = dict(density=0.22, p=0.25, speed=1, pause=False, hold=0, k=0)
rng = np.random.default_rng()

ang = np.pi / 2 - 2 * np.pi * np.arange(L) / L     # 시계 방향
X, Y = np.cos(ang), np.sin(ang)

# ---------------- 화면 ----------------
# 도로(어두운 회색)와 확실히 구분되는 밝은 색: 빨강(정지) → 주황 → 노랑 → 연두 → 하늘색(빠름)
CMAP = LinearSegmentedColormap.from_list("speed", ["#ff1a1a", "#ff8c00", "#ffee00", "#9dff00", "#00e5ff"])
fig = plt.figure(figsize=(6.5, 8))
ax = fig.add_axes([0.03, 0.30, 0.94, 0.66])
ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25)
ax.plot(X, Y, color="#3a3a3a", lw=24, zorder=1)
scat = ax.scatter([], [], s=85, c=[], cmap=CMAP, vmin=0, vmax=VMAX, edgecolors="white", linewidths=1.2, zorder=3)
info = ax.text(0, 0, "", ha="center", va="center", fontsize=12, linespacing=1.7)
ax.set_title("유령정체  (빨강=정지 → 노랑 → 하늘색=빠름)")


# ---------------- 모델 ----------------
def reset(_=None):
    global pos, vel
    n = max(2, int(L * S["density"]))
    pos, vel = np.sort(rng.choice(L, n, replace=False)), np.zeros(n, int)


def step():
    global pos, vel
    gap = (np.roll(pos, -1) - pos - 1) % L                        # 앞차까지 빈 칸
    vel = np.minimum(np.minimum(vel + 1, VMAX), gap)              # 가속 + 안전거리
    vel = vel - ((rng.random(len(vel)) < S["p"]) & (vel > 0))     # 무작위 감속
    if S["hold"] > 0:                                             # 급브레이크
        vel[S["k"]] = 0
        S["hold"] -= 1
    pos = (pos + vel) % L


# ---------------- 버튼 ----------------
def change(key, delta, lo, hi, need_reset=False):
    def f(_):
        S[key] = round(min(hi, max(lo, S[key] + delta)), 2)
        if need_reset:
            reset()
    return f


def kick(_):
    S["k"], S["hold"] = rng.integers(len(pos)), 4


def toggle(_):
    S["pause"] = not S["pause"]


# (라벨, 동작) 3열 x 3행
BTNS = [
    [("밀도 −", change("density", -.02, .04, .8, True)), ("밀도 +", change("density", .02, .04, .8, True)), ("차 1대 급브레이크", kick)],
    [("감속확률 −", change("p", -.05, 0, 1)), ("감속확률 +", change("p", .05, 0, 1)), ("일시정지 / 재생", toggle)],
    [("속도 −", change("speed", -1, 1, 6)), ("속도 +", change("speed", 1, 1, 6)), ("초기화", reset)],
]
buttons = []                                         # 참조 유지 필수
for r, row in enumerate(BTNS):
    for c, (label, fn) in enumerate(row):
        b = Button(fig.add_axes([0.04 + c * 0.32, 0.20 - r * 0.075, 0.29, 0.06]), label)
        b.on_clicked(fn)
        buttons.append(b)

reset()


def update(_):
    if not S["pause"]:
        for _ in range(S["speed"]):
            step()
    scat.set_offsets(np.c_[X[pos], Y[pos]])
    scat.set_array(vel)
    info.set_text(f"밀도 {S['density']:.2f}   감속확률 {S['p']:.2f}   속도 x{S['speed']}\n"
                  f"평균속도 {vel.mean():.1f}\n정체 차량 {np.mean(vel <= 1) * 100:.0f}%")
    return scat, info


anim = FuncAnimation(fig, update, interval=20, blit=True, cache_frame_data=False)
plt.show()
