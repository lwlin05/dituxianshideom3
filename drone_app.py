import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import time
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="无人机智能化应用", layout="wide")

with st.sidebar:
    st.markdown("### 🧭 导航")
    page = st.radio(
        "功能页面",
        ["🗺️ 航线规划", "📡 飞行监控"],
        index=0
    )

# ===================== 航线规划页面 =====================
if page == "🗺️ 航线规划":
    st.title("分组作业3-项目Demo")
    st.subheader("🗺️ 地图")

    # 坐标系转换函数
    def wgs84_to_gcj02(lon, lat):
        a = 6378245.0
        ee = 0.0066934216229659433
        dLat = -100.0 + 2.0 * lon + 3.0 * lat + 0.2 * lat * lat + 0.1 * lon * lat + 0.2 * math.sqrt(math.fabs(lon))
        dLon = 300.0 + lon + 2.0 * lat + 0.1 * lon * lon + 0.1 * lon * lat + 0.1 * math.sqrt(math.fabs(lon))
        radLat = lat / 180.0 * math.pi
        magic = math.sin(radLat)
        magic = 1 - ee * magic * magic
        sqrtMagic = math.sqrt(magic)
        dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * math.pi / 180.0)
        dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * math.pi / 180.0)
        return lon + dLon, lat + dLon

    # 初始化会话状态（和截图示例坐标一致）
    if "a_lat" not in st.session_state:
        st.session_state.a_lat = 32.2322
        st.session_state.a_lon = 118.749
        st.session_state.b_lat = 32.2343
        st.session_state.b_lon = 118.749
        st.session_state.sys_state = {"A": False, "B": False}

    # 分栏布局：地图 + 控制面板
    col_map, col_ctrl = st.columns([3, 1])

    with col_ctrl:
        st.markdown("### ⚙️ 控制面板")
        st.markdown("输入坐标系: GCJ-02")

        # 起点A（和截图完全一致）
        st.markdown("##### 📍 起点A")
        a_lat = st.number_input("纬度", value=st.session_state.a_lat, format="%.6f", key="a_lat_in")
        a_lon = st.number_input("经度", value=st.session_state.a_lon, format="%.6f", key="a_lon_in")
        if st.button("设置A点", key="set_a"):
            st.session_state.a_lat = a_lat
            st.session_state.a_lon = a_lon
            st.session_state.sys_state["A"] = True
            st.success("✅ A点已设")

        # 终点B（和截图完全一致）
        st.markdown("##### 📍 终点B")
        b_lat = st.number_input("纬度", value=st.session_state.b_lat, format="%.6f", key="b_lat_in")
        b_lon = st.number_input("经度", value=st.session_state.b_lon, format="%.6f", key="b_lon_in")
        if st.button("设置B点", key="set_b"):
            st.session_state.b_lat = b_lat
            st.session_state.b_lon = b_lon
            st.session_state.sys_state["B"] = True
            st.success("✅ B点已设")

        # 飞行参数（和截图一致）
        st.markdown("##### ✈️ 飞行参数")
        height = st.slider("设定飞行高度(m)", 0, 200, 50)

        # 坐标系设置（和截图完全一致）
        st.markdown("### ⚙️ 坐标系设置")
        coord = st.radio("输入坐标系", ["WGS-84", "GCJ-02(高德/百度)"], index=1)

        # 系统状态（和截图完全一致）
        st.markdown("### 📊 系统状态")
        if st.session_state.sys_state["A"]:
            st.success("A点已设")
        else:
            st.info("A点未设")
        if st.session_state.sys_state["B"]:
            st.success("B点已设")
        else:
            st.info("B点未设")

    with col_map:
        # 地图中心（南京科技职业学院 GCJ-02 坐标）
        SCHOOL_LAT = 32.2332
        SCHOOL_LON = 118.749
        m = folium.Map(location=[SCHOOL_LAT, SCHOOL_LON], zoom_start=16, tiles=None)

        # 高德卫星图 + 路网图（和截图的卫星地图一致）
        folium.TileLayer(
            tiles="https://webst01.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
            attr="高德地图",
            name="高德卫星图"
        ).add_to(m)
        folium.TileLayer(
            tiles="https://webst01.is.autonavi.com/appmaptile?style=7&x={x}&y={y}&z={z}",
            attr="高德地图",
            name="高德路网图"
        ).add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)

        # 坐标转换处理
        if coord == "WGS-84":
            alon, alat = wgs84_to_gcj02(a_lon, a_lat)
            blon, blat = wgs84_to_gcj02(b_lon, b_lat)
        else:
            alon, alat = a_lon, a_lat
            blon, blat = b_lon, b_lat

        # 绘制A/B点（顺序必须是[纬度, 经度]）
        folium.Marker(location=[alat, alon], popup="起点A", icon=folium.Icon(color="red")).add_to(m)
        folium.Marker(location=[blat, blon], popup="终点B", icon=folium.Icon(color="green")).add_to(m)

        # 绘制航线（和截图一致）
        folium.PolyLine(locations=[[alat, alon], [blat, blon]], color="blue", weight=3).add_to(m)

        # 显示地图
        st_folium(m, width=800, height=600)

    st.divider()
    st.caption("💡 滚轮放大可查看校园二维样貌，方便后期障碍物圈选")

# ===================== 飞行监控页面 =====================
elif page == "📡 飞行监控":
    st.title("📡 飞行监控 - 无人机心跳包")

    INTERVAL = 1
    TIMEOUT = 3

    # 初始化会话状态
    if "heartbeat" not in st.session_state:
        st.session_state.heartbeat = []
        st.session_state.last_recv = time.time()
        st.session_state.seq = 0
        st.session_state.running = True

    # 自动心跳逻辑
    if st.session_state.running:
        st.session_state.seq += 1
        now = time.time()
        st.session_state.last_recv = now
        st.session_state.heartbeat.append({
            "序号": st.session_state.seq,
            "时间": datetime.fromtimestamp(now).strftime("%H:%M:%S")
        })
        if len(st.session_state.heartbeat) > 50:
            st.session_state.heartbeat.pop(0)

    # 超时检测
    dt = time.time() - st.session_state.last_recv
    if dt > TIMEOUT:
        st.error(f"⚠️ 连接超时！已 {dt:.1f} 秒未收到心跳")
    else:
        st.success(f"✅ 心跳正常 | 上次心跳 {dt:.1f} 秒前")

    # 心跳包数据列表
    st.subheader("📋 心跳包数据")
    df = pd.DataFrame(st.session_state.heartbeat)
    st.dataframe(df, use_container_width=True)

    # 心跳趋势图
    st.subheader("📈 心跳序号趋势")
    if not df.empty:
        st.line_chart(df, x="时间", y="序号", use_container_width=True)

    # 控制按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("开始心跳"):
            st.session_state.running = True
    with col2:
        if st.button("停止心跳"):
            st.session_state.running = False

    # 自动刷新
    if st.session_state.running:
        time.sleep(INTERVAL)
        st.rerun()