import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="无人机智能化应用", layout="wide")

# 初始化坐标（南京科技职业学院）
if "a_lat" not in st.session_state:
    st.session_state.a_lat = 32.2322
    st.session_state.a_lon = 118.7490
    st.session_state.b_lat = 32.2343
    st.session_state.b_lon = 118.7490

# 侧边栏
with st.sidebar:
    st.markdown("### 🧭 导航")
    page = st.radio(
        "功能页面",
        ["🗺️ 航线规划", "📡 飞行监控"],
        index=0
    )

# ====================== 航线规划（folium 地图）======================
if page == "🗺️ 航线规划":
    st.title("分组作业3-项目Demo")
    st.subheader("🗺️ 地图")

    col_map, col_ctrl = st.columns([3, 1])

    with col_ctrl:
        st.markdown("### ⚙️ 控制面板")
        st.markdown("**输入坐标系: GCJ-02**")

        st.markdown("##### 📍 起点A")
        st.number_input("纬度", format="%.6f", key="a_lat")
        st.number_input("经度", format="%.6f", key="a_lon")

        st.markdown("##### 📍 终点B")
        st.number_input("纬度", format="%.6f", key="b_lat")
        st.number_input("经度", format="%.6f", key="b_lon")

        st.markdown("##### ✈️ 飞行参数")
        st.slider("设定飞行高度(m)", 0, 200, 50)

        st.markdown("### ⚙️ 坐标系设置")
        st.radio("输入坐标系", ["WGS-84", "GCJ-02(高德/百度)"], index=1)

        st.markdown("### 📊 系统状态")
        st.success("A点已设")
        st.success("B点已设")

    with col_map:
        # folium 地图（学校中心）
        m = folium.Map(location=[32.2332, 118.7490], zoom_start=17, tiles="https://webst01.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}", attr="高德地图")
        
        # A点
        folium.Marker(
            location=[st.session_state.a_lat, st.session_state.a_lon],
            popup="起点A",
            icon=folium.Icon(color="red")
        ).add_to(m)

        # B点
        folium.Marker(
            location=[st.session_state.b_lat, st.session_state.b_lon],
            popup="终点B",
            icon=folium.Icon(color="green")
        ).add_to(m)

        # 航线
        folium.PolyLine(
            locations=[
                [st.session_state.a_lat, st.session_state.a_lon],
                [st.session_state.b_lat, st.session_state.b_lon]
            ],
            color="blue",
            weight=3
        ).add_to(m)

        st_folium(m, width=900, height=650)

# ====================== 飞行监控 ======================
elif page == "📡 飞行监控":
    st.title("📡 飞行监控")

    if "heartbeat" not in st.session_state:
        st.session_state.heartbeat = []
        st.session_state.seq = 0
        st.session_state.running = True

    if st.session_state.running:
        st.session_state.seq += 1
        now = time.time()
        st.session_state.heartbeat.append({
            "序号": st.session_state.seq,
            "时间": datetime.fromtimestamp(now).strftime("%H:%M:%S")
        })
        if len(st.session_state.heartbeat) > 30:
            st.session_state.heartbeat.pop(0)

    st.subheader("心跳包数据")
    df = pd.DataFrame(st.session_state.heartbeat)
    st.dataframe(df, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("开始心跳"):
            st.session_state.running = True
    with c2:
        if st.button("停止心跳"):
            st.session_state.running = False

    if st.session_state.running:
        time.sleep(1)
        st.rerun()