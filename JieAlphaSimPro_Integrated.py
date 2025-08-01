import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests, pandas as pd, yfinance as yf, mplfinance as mpf, plotly.graph_objects as go
import os, json, io

st.set_page_config(page_title="JieAlpha 策略评分平台", layout="wide")
st.title("🧠 JieAlphaSimPro · 多股行为 + 趋势 + 资金 综合评分系统")
with st.sidebar:
    codes_input = st.text_area("📥 输入股票代码（逗号/换行分隔）", "300750,600519,688012")
    codes = [x.strip() for x in codes_input.replace("\n", ",").split(",") if x.strip()]

    filter_mode = st.selectbox("🧪 策略筛选器", ["洗盘+真涨", "鼎沸冲高", "横盘潜伏", "不过滤"])
    auto_refresh = st.checkbox("🔄 自动刷新页面", value=True)
    refresh_interval = st.slider("⏱️ 自动刷新频率（秒）", 10, 60, 30)

    use_etf_template = st.checkbox("📋 使用ETF模板", value=True)
    export_csv = st.checkbox("📁 导出评分结果CSV", value=False)
    show_log = st.checkbox("🧰 显示后台日志面板", value=False)
    show_etf_heatmap = st.checkbox("🔥 显示ETF热度榜单", value=False)

    show_radar = st.checkbox("📊 显示雷达图", value=True)
    show_kline = st.checkbox("📈 显示 K 线图", value=True)
    show_explain = st.checkbox("📘 显示评分解释", value=True)

if auto_refresh:
    st_autorefresh(interval=refresh_interval * 1000, key="autoRefresh")
def load_etf_template():
    try:
        with open("etf_templates.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def fetch_etf_ranking():
    etf_codes = ["512480", "516950", "159819", "515790", "516850"]
    result = []
    for code in etf_codes:
        prefix = 'sh' if code.startswith('6') else 'sz'
        url = f"http://hq.sinajs.cn/list={prefix}{code}"
        try:
            res = requests.get(url, headers={"Referer": "https://finance.sina.com.cn"}, timeout=5)
            res.encoding = 'gbk'
            parts = res.text.split('"')[1].split(",")
            name, now, prev = parts[0], float(parts[3]), float(parts[2])
            chg = round((now - prev) / prev * 100, 2)
            result.append({"代码": code, "名称": name, "涨跌幅(%)": chg})
        except:
            pass
    df = pd.DataFrame(result).sort_values("涨跌幅(%)", ascending=False)
    return df
def fetch_snapshot(code): ...
def score_behavior_pattern(q): ...
def compute_trend_score(q): ...
def compute_money_score(q): ...
def plot_behavior_radar(scores): ...
def plot_kline(code): ...
def filter_signals(s, mode): ...
def read_log_tail(log_path, lines=20):
    if not os.path.exists(log_path): return "暂无日志"
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        return "\n".join(f.readlines()[-lines:])
if use_etf_template:
    etf_templates = load_etf_template()
    selected_template = st.sidebar.selectbox("🎯 选择ETF组合", list(etf_templates.keys()))
    codes = etf_templates.get(selected_template, [])

st.subheader("📊 多股策略评分结果")
results = []

for code in codes:
    q = fetch_snapshot(code)
    s, e = score_behavior_pattern(q)
    trend = compute_trend_score(q)
    money = compute_money_score(q)
    combined = {
        "横盘评分": s.get("横盘评分", 0),
        "洗盘评分": s.get("洗盘评分", 0),
        "趋势评分": trend,
        "资金评分": money
    }
    if filter_signals(combined, filter_mode):
        row = {
            "代码": q.get("代码", ""),
            "名称": q.get("名称", ""),
            "现价": q.get("现价", ""),
            **combined
        }
        results.append((row, combined, e))
if results:
    st.dataframe([r[0] for r in results])
    for row, scores, explain in results:
        st.markdown(f"---\n### {row['名称']} ({row['代码']})")
        if show_radar:
            st.plotly_chart(plot_behavior_radar(scores), use_container_width=True)
        if show_kline:
            plot_kline(row["代码"])
        if show_explain:
            st.markdown("📘 **评分解释**")
            for k, v in explain.items():
                st.markdown(f"- {k}：{v}")

    if export_csv:
        df_export = pd.DataFrame([r[0] for r in results])
        st.download_button(
            label="📁 下载评分结果 CSV",
            data=df_export.to_csv(index=False).encode('utf-8'),
            file_name="JieAlpha评分结果.csv",
            mime="text/csv"
        )

if show_log:
    st.expander("🧰 Streamlit运行日志").code(read_log_tail("streamlit_launch.log"), language="bash")

if show_etf_heatmap:
    st.subheader("🔥 ETF 热度榜单")
    st.dataframe(fetch_etf_ranking())
