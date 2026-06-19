import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 設置網頁寬螢幕配置
st.set_page_config(page_title="通用剛體力學與摩擦分析系統", layout="wide")

st.title("📘 通用型剛體力學平衡與乾摩擦分析引擎")
st.caption("國立勤益科技大學 智慧自動化工程系 — 期末加分專題")

st.markdown("""
本系統為**整合型通用二維剛體力學分析引擎**。
系統將所有摩擦力與幾何力矩問題抽象化為通用剛體模型，自動求解法向力分配、極限庫倫摩擦力，並判定系統平衡狀態。
""")

# ==================== 側邊欄：通用幾何與力學參數輸入 ====================
st.sidebar.header("🚀 通用力學幾何參數設定")

st.sidebar.subheader("1. 剛體幾何與跨距設定 (公尺 m)")
L_dist = st.sidebar.number_input("兩端支承點（或輪軸）總跨距 (L)", min_value=0.01, value=1.5, step=0.1)
x_G = st.sidebar.number_input("左支承(B)到重心(G)的水平距離 (x_G)", min_value=0.0, value=0.5, step=0.1)
d_force = st.sidebar.number_input("主動外力 P 到轉動中心的垂直力臂 (d)", min_value=0.0, value=0.2, step=0.05)

st.sidebar.subheader("2. 系統荷重與主動外力 (N 或 kN)")
W_mass = st.sidebar.number_input("系統總垂直荷重 / 重力 (W)", min_value=0.0, value=1.0, step=1.0)
P_force = st.sidebar.number_input("施加之水平驅動外力 (P)", min_value=0.0, value=1.0, step=1.0)

st.sidebar.subheader("3. 接觸面摩擦物理性質")
mu_s = st.sidebar.number_input("靜摩擦係數 (μs)", min_value=0.0, max_value=1.0, value=0.4, step=0.05)
num_faces = st.sidebar.number_input("有效摩擦接觸面數量 (n)", min_value=1, value=1, step=1)

# ==================== 後端通用剛體力學矩陣求解引擎 ====================
# 使用絕對力矩差值模型，完美相容各種推力方向與力矩正負號
N_A_calc = abs((W_mass * x_G) - (P_force * d_force)) / L_dist

# 浮點數防呆校正：若數值極小則精準歸零
if N_A_calc <= 1e-4:
    N_A_calc = 0.0

N_B_calc = W_mass - N_A_calc

# 計算系統總有效正向力與庫倫摩擦極限
N_total = (abs(N_A_calc) + abs(N_B_calc)) * num_faces
F_max = mu_s * N_total
F_required = abs(P_force)

# 狀態判定決策樹
status_color = "green"
if F_required < F_max:
    motion_status = "【靜止平衡狀態 (Static Equilibrium)】"
    status_desc = f"所需摩擦力 ({F_required:.2f}) 未超過最大靜摩擦力上限 ({F_max:.2f})。系統安全靜止。"
elif np.isclose(F_required, F_max, atol=1e-2):
    motion_status = "【臨界即將滑動 / 自鎖臨界點 (Impending Motion)】"
    status_color = "orange"
    status_desc = "外力驅動剪力剛好等於最大靜摩擦力上限，系統處於臨界滑動狀態。"
else:
    motion_status = "【發生相對運動 / 動態滑動 (Slipping)】"
    status_color = "red"
    status_desc = f"外力驅動剪力 ({F_required:.2f}) 已超摩擦力極限上限 ({F_max:.2f})，結構發生滑動破壞。"

# ==================== 前端全自動動態呈現 ====================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 剛體力學運算與判定矩陣")
    st.markdown(f"### 系統判定狀態： :{status_color}[{motion_status}]")
    st.info(f"💡 **狀態解讀**：{status_desc}")
        
    st.markdown("#### 📢 剛體支承反力矩陣 (支點反力)")
    c1, c2 = st.columns(2)
    c1.metric("A 處垂直正向力 (N_A)", f"{N_A_calc:.2f}")
    c2.metric("B 處垂直正向力 (N_B)", f"{N_B_calc:.2f}")
    
    st.markdown("#### 📢 庫倫摩擦力判定矩陣")
    c3, c4 = st.columns(2)
    c3.metric("極限靜摩擦力上限 (F_max)", f"{F_max:.2f}")
    c4.metric("實際平衡所需摩擦力 (F_req)", f"{F_required:.2f}")

    st.markdown("#### 📝 通用剛體靜力學平衡方程推導 (Step-by-Step)")
    st.write(f"1. 對 B 點取力矩平衡方程分析求解：")
    st.write(f"   |({W_mass:.2f} × {x_G:.2f}) - ({P_force:.2f} × {d_force:.2f})| - (N_A × {L_dist:.2f}) = 0  👉 求解得：N_A = {N_A_calc:.2f}")
    st.write(f"2. 垂直方向受力平衡分析 (ΣF_y = 0)：")
    st.write(f"   N_A + N_B - W = 0  👉 求解得：N_B = {N_B_calc:.2f}")
    st.write(f"3. 庫倫乾摩擦極限與狀態評判：")
    st.write(f"   總有效正向力 ΣN = {N_total:.2f}，極限靜摩擦力上限 F_max = {F_max:.2f}，實際所需外力 F_req = {F_required:.2f}")

with col2:
    st.subheader("🎨 通用剛體受力幾何體 (FBD)")
    
    # 建立畫布
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_aspect('equal')
    
    # 畫出地面基線
    ax.plot([-1, 4], [0, 0], 'k-', lw=4)
    
    # 畫出通用剛體主體
    rect = plt.Rectangle((0.2, 0.05), 2.6, 1.2, color='whitesmoke', ec='teal', lw=2, alpha=0.8)
    ax.add_patch(rect)
    
    # 正確向量箭頭：支點反力由下往上頂 (綠色)
    ax.quiver(0.5, -0.6, 0, 0.6, angles='xy', scale_units='xy', scale=1, color='green', width=0.015)
    ax.text(0.6, -0.4, 'N_B', color='green', fontsize=11, fontweight='bold')
    
    ax.quiver(2.5, -0.6, 0, 0.6, angles='xy', scale_units='xy', scale=1, color='green', width=0.015)
    ax.text(2.6, -0.4, 'N_A', color='green', fontsize=11, fontweight='bold')
    
    # 正確向量箭頭：外力 P 由左向右推 (紫色)
    ax.quiver(-0.8, 0.9, 0.9, 0, angles='xy', scale_units='xy', scale=1, color='purple', width=0.015)
    ax.text(-0.8, 1.1, 'P (Force)', color='purple', fontsize=11, fontweight='bold')
    
    # 正確向量箭頭：重力 W 垂直向下 (紅色)
    ax.quiver(1.5, 0.9, 0, -0.8, angles='xy', scale_units='xy', scale=1, color='red', width=0.015)
    ax.text(1.6, 0.3, 'W (Gravity)', color='red', fontsize=11, fontweight='bold')
    
    ax.set_xlim(-1.5, 4)
    ax.set_ylim(-1.2, 2.2)
    ax.axis('off')
    
    # 顯示圖表
    st.pyplot(fig)