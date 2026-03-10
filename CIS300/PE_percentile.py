import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
import time

import numpy as np

# ==========================================
# 1. 核心配置 (USER CONFIGURATION)
# ==========================================
INDEX_NAME = "沪深300"  # 指数名称 (支持: "沪深300", "中证500", "创业板50" 等)
YEARS_BACK = 15  # 回溯 5 年的历史数据计算百分位
SELL_THRESHOLD = 80.0  # 卖出阈值：估值高于历史 80% 的时间
BUY_THRESHOLD = 40.0  # 买入阈值：估值低于历史 40% 的时间

# PE 百分位参考线
PERCENTILE_LEVELS = [80, 60, 40, 20]

# 邮件设置 (请使用应用专用密码)
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"
RECEIVER_EMAIL = "target_email@gmail.com"

# 图表均线设置
CHART_FILENAME = "pe_valuation_trend.png"
SHORT_MA = 60
LONG_MA = 120

# 简化版 CAPE: 3年滚动平均PE
CAPE_ROLLING_YEARS = 3
CAPE_ROLLING_DAYS = CAPE_ROLLING_YEARS * 252  # 约756个交易日

# CAPE 偏离度阈值
CAPE_DEVIATION_HIGH = 15.0   # 偏离 > 15% 视为高估
CAPE_DEVIATION_LOW = -15.0   # 偏离 < -15% 视为低估


# ==========================================
# 2. 核心功能函数
# ==========================================

def fetch_pe_data(index_name, years, max_retries=3):
    """获取真实市盈率(P/E)数据并截取对应的时间窗口.
    额外获取 CAPE_ROLLING_YEARS 年数据以保证滚动平均有完整覆盖.
    """
    print(f"正在获取 {index_name} 的真实市盈率估值数据...")
    for attempt in range(max_retries):
        try:
            # 使用 AkShare 最新的指数市盈率函数
            df = ak.stock_index_pe_lg(symbol=index_name)

            # 格式化日期
            df['trade_date'] = pd.to_datetime(df['日期'])
            df = df.sort_values('trade_date')

            # 我们使用 "滚动市盈率" (PE TTM) 作为最科学的估值指标
            df['pe'] = pd.to_numeric(df['滚动市盈率'])

            # 先在全量数据上计算3年滚动平均PE (简化版CAPE)
            df['pe_cape'] = df['pe'].rolling(window=CAPE_ROLLING_DAYS, min_periods=1).mean()

            # 再筛选过去 N 年的数据用于展示
            start_date = df['trade_date'].max() - relativedelta(years=years)
            df = df[df['trade_date'] >= start_date].copy()

            return df
        except Exception as e:
            print(f"数据获取失败 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print("等待 10 秒后重试...")
                time.sleep(10)
            else:
                return None


def fetch_bond_yield_10y(max_retries=3):
    """获取中国10年期国债最新收益率 (%).
    返回收益率的小数形式, 例如 1.75% -> 0.0175
    """
    print("正在获取中国10年期国债收益率...")
    for attempt in range(max_retries):
        try:
            df = ak.bond_zh_us_rate()
            df = df.dropna(subset=['中国国债收益率10年'])
            latest_yield_pct = float(df['中国国债收益率10年'].iloc[-1])
            print(f"最新10年期国债收益率: {latest_yield_pct:.4f}%")
            return latest_yield_pct / 100.0  # 转为小数
        except Exception as e:
            print(f"国债收益率数据获取失败 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(10)
            else:
                return None


def analyze_valuation(df):
    """计算当前PE、百分位、均线及各百分位对应的PE值"""
    current_pe = df['pe'].iloc[-1]
    pe_history = df['pe'].dropna()

    # 计算当前 PE 在过去5年中的百分位
    percentile = stats.percentileofscore(pe_history, current_pe)

    # 计算各参考百分位对应的 PE 值
    pe_percentile_values = {}
    for p in PERCENTILE_LEVELS:
        pe_percentile_values[p] = np.percentile(pe_history, p)

    # 计算均线
    df['MA_Short'] = df['pe'].rolling(window=SHORT_MA).mean()
    df['MA_Long'] = df['pe'].rolling(window=LONG_MA).mean()

    return current_pe, percentile, pe_percentile_values, df


def calculate_erp(current_pe, bond_yield_decimal):
    """计算股权风险溢价 (Equity Risk Premium).
    ERP = 盈利收益率 (1/PE) - 10年期国债收益率
    """
    earnings_yield = 1.0 / current_pe
    erp = earnings_yield - bond_yield_decimal
    return earnings_yield, erp


def calculate_cape_deviation(current_pe, cape_value):
    """计算当前PE相对3年滚动均值PE的偏离度 (%)."""
    if cape_value is None or cape_value == 0:
        return None
    return (current_pe - cape_value) / cape_value * 100.0


def compute_composite_signal(percentile, cape_deviation, erp):
    """综合三因子分析: 百分位 + CAPE偏离度 + ERP.
    返回 (signal_label, signal_detail, confidence).

    评分规则:
      - 百分位:  >80 → -2(bearish), 60-80 → -1, 40-60 → 0, 20-40 → +1, <20 → +2(bullish)
      - CAPE偏离: >15% → -1, -15% ~ 15% → 0, <-15% → +1
      - ERP:      <0 → -1, 0~3% → 0, 3~6% → +1, >6% → +2
    """
    score = 0
    factors = []

    # 因子 1: 百分位
    if percentile >= 80:
        score -= 2; factors.append(f"百分位 {percentile:.0f}% (极高)")
    elif percentile >= 60:
        score -= 1; factors.append(f"百分位 {percentile:.0f}% (偏高)")
    elif percentile >= 40:
        score += 0; factors.append(f"百分位 {percentile:.0f}% (中性)")
    elif percentile >= 20:
        score += 1; factors.append(f"百分位 {percentile:.0f}% (偏低)")
    else:
        score += 2; factors.append(f"百分位 {percentile:.0f}% (极低)")

    # 因子 2: CAPE 偏离度
    if cape_deviation is not None:
        if cape_deviation > CAPE_DEVIATION_HIGH:
            score -= 1; factors.append(f"CAPE偏离 +{cape_deviation:.1f}% (高估)")
        elif cape_deviation < CAPE_DEVIATION_LOW:
            score += 1; factors.append(f"CAPE偏离 {cape_deviation:.1f}% (低估)")
        else:
            factors.append(f"CAPE偏离 {cape_deviation:+.1f}% (正常)")

    # 因子 3: ERP
    if erp is not None:
        erp_pct = erp * 100
        if erp_pct > 6:
            score += 2; factors.append(f"ERP {erp_pct:.1f}% (极具吸引力)")
        elif erp_pct > 3:
            score += 1; factors.append(f"ERP {erp_pct:.1f}% (有吸引力)")
        elif erp_pct > 0:
            factors.append(f"ERP {erp_pct:.1f}% (中性)")
        else:
            score -= 1; factors.append(f"ERP {erp_pct:.1f}% (股市偏贵)")

    # 综合判定
    if score >= 4:
        label = "🟢 强烈买入"
    elif score >= 2:
        label = "✅ 买入"
    elif score >= -1:
        label = "⚪ 中性/持有"
    elif score >= -3:
        label = "🟡 卖出"
    else:
        label = "🔴 强烈卖出"

    # 置信度: 看因子方向是否一致
    total_factors = 2 + (1 if cape_deviation is not None else 0) + (1 if erp is not None else 0)
    confidence = f"{abs(score)}/{total_factors + 1}"

    return label, factors, score, confidence


def generate_chart(df, current_pe, percentile, pe_percentile_values, erp_info=None):
    """生成并保存市盈率趋势图，包含百分位参考线和ERP信息"""
    # 解决 matplotlib 中文显示问题
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(14, 7))

    # 绘制 P/E 和均线
    ax.plot(df['trade_date'], df['pe'], label='滚动市盈率 (PE TTM)', color='dodgerblue', alpha=0.5)
    ax.plot(df['trade_date'], df['MA_Short'], label=f'{SHORT_MA}日均线', color='orange', linewidth=1.5)
    ax.plot(df['trade_date'], df['MA_Long'], label=f'{LONG_MA}日均线', color='darkred', linewidth=2)

    # 绘制3年滚动平均PE (简化版CAPE)
    if 'pe_cape' in df.columns:
        ax.plot(df['trade_date'], df['pe_cape'],
                label=f'{CAPE_ROLLING_YEARS}年滚动均值 PE (简化CAPE): {df["pe_cape"].iloc[-1]:.2f}',
                color='purple', linewidth=2.5, linestyle='-', alpha=0.85)

    # 添加当前位置线
    ax.axhline(y=current_pe, color='black', linestyle='--', linewidth=1.5,
               label=f'当前 PE: {current_pe:.2f} ({percentile:.1f}%分位)')

    # 绘制各百分位参考线
    percentile_colors = {80: '#e74c3c', 60: '#e67e22', 40: '#27ae60', 20: '#2980b9'}
    percentile_styles = {80: '-.', 60: ':', 40: ':', 20: '-.'}
    for p, pe_val in pe_percentile_values.items():
        color = percentile_colors.get(p, 'gray')
        style = percentile_styles.get(p, ':')
        ax.axhline(y=pe_val, color=color, linestyle=style, alpha=0.7, linewidth=1.2,
                   label=f'{p}%分位 PE: {pe_val:.2f}')

    # 构建标题
    title = f'{INDEX_NAME} {YEARS_BACK}年市盈率 (PE TTM) 估值趋势'
    if erp_info:
        earnings_yield, erp, bond_yield = erp_info
        title += f'\nERP={erp*100:.2f}%  (盈利收益率{earnings_yield*100:.2f}% − 国债{bond_yield*100:.2f}%)'

    ax.set_title(title, fontsize=14)
    ax.set_ylabel('市盈率 (倍)')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, linestyle=':', alpha=0.6)

    # 格式化 X 轴
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(CHART_FILENAME, dpi=200)
    plt.close()
    return CHART_FILENAME


def send_email_with_chart(subject, body, attachment_path):
    """发送包含图表附件的邮件警报"""
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            img_data = f.read()
        image = MIMEImage(img_data, name=os.path.basename(attachment_path))
        msg.attach(image)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("✅ 预警邮件发送成功！")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

def save_markdown_report(current_pe, percentile, signal_label, signal_score, signal_factors, extra_analysis):
    """生成 Markdown 报告用于 Dashboard 展示"""
    today = datetime.now().strftime("%Y-%m-%d")
    report_name = f"CSI300_report_{today}.md"

    # 清理信号标签，去表情
    clean_signal_label = signal_label.split(" ", 1)[-1] if " " in signal_label else signal_label

    with open(report_name, "w", encoding="utf-8") as f:
        f.write(f"# CSI 300 (沪深300) Valuation Report\n\n")
        f.write(f"## Composite Signal\n")
        # 需要符合 run_all.py 的正则表达式
        # **<< 强烈卖出 >>** — Score: -4
        f.write(f"**<< {clean_signal_label} >>** — Score: {signal_score}\n\n")
        
        f.write(f"## Valuation Metrics\n")
        f.write(f"- **Current PE TTM**: {current_pe:.2f}\n")
        f.write(f"- **Historical Percentile**: {percentile:.2f}%\n")
        
        f.write(f"\n## Key Factors\n")
        for factor in signal_factors:
            f.write(f"- {factor}\n")
            
        f.write(f"\n## Detailed Analysis\n")
        f.write(f"```\n{extra_analysis}\n```\n")
        
    print(f"  [REPORT] Saved: {report_name}")



# ==========================================
# 3. 主执行流
# ==========================================

def main():
    df = fetch_pe_data(INDEX_NAME, YEARS_BACK)
    if df is None or df.empty:
        print("未能获取数据，退出程序。")
        return

    current_pe, percentile, pe_percentile_values, df = analyze_valuation(df)

    # 打印 PE 百分位信息
    cape_value = df['pe_cape'].iloc[-1] if 'pe_cape' in df.columns else None
    print(f"\n{'='*55}")
    print(f"  指数: {INDEX_NAME} | 当前 PE TTM: {current_pe:.2f}")
    if cape_value is not None:
        print(f"  {CAPE_ROLLING_YEARS}年滚动均值 PE (简化CAPE): {cape_value:.2f}")
    print(f"  当前所处百分位: {percentile:.2f}%")
    print(f"{'='*55}")
    print(f"  PE 百分位参考值 (过去{YEARS_BACK}年):")
    for p in sorted(pe_percentile_values.keys(), reverse=True):
        marker = " ◀ 当前" if abs(percentile - p) < 10 else ""
        print(f"    {p:3d}%分位 PE = {pe_percentile_values[p]:.2f}{marker}")
    print(f"{'='*55}")

    # CAPE 偏离度分析
    cape_deviation = calculate_cape_deviation(current_pe, cape_value)
    if cape_deviation is not None:
        print(f"\n  📏 CAPE 偏离度分析:")
        print(f"    当前 PE TTM:       {current_pe:.2f}")
        print(f"    {CAPE_ROLLING_YEARS}年滚动均值 PE:   {cape_value:.2f}")
        print(f"    偏离度:            {cape_deviation:+.2f}%")
        if cape_deviation > CAPE_DEVIATION_HIGH:
            print(f"    ⚠️  偏离 > +{CAPE_DEVIATION_HIGH}%，当前PE显著高于{CAPE_ROLLING_YEARS}年均值，短期估值过热")
        elif cape_deviation < CAPE_DEVIATION_LOW:
            print(f"    💡 偏离 < {CAPE_DEVIATION_LOW}%，当前PE显著低于{CAPE_ROLLING_YEARS}年均值，可能被低估")
        else:
            print(f"    ✅ 偏离在正常范围内 (±{CAPE_DEVIATION_HIGH}%)")
        print(f"{'='*55}")

    # 计算 ERP (股权风险溢价)
    erp_info = None
    erp_value = None
    bond_yield = fetch_bond_yield_10y()
    if bond_yield is not None:
        earnings_yield, erp_value = calculate_erp(current_pe, bond_yield)
        erp_info = (earnings_yield, erp_value, bond_yield)
        print(f"\n  📊 股权风险溢价 (ERP) 分析:")
        print(f"    盈利收益率 (1/PE):  {earnings_yield*100:.2f}%")
        print(f"    10年期国债收益率:   {bond_yield*100:.2f}%")
        print(f"    ERP = {earnings_yield*100:.2f}% − {bond_yield*100:.2f}% = {erp_value*100:.2f}%")
        if erp_value > 0.06:
            print(f"    💡 ERP > 6%，股市极具吸引力，处于历史低估区域")
        elif erp_value > 0.03:
            print(f"    💡 ERP 在 3%-6% 之间，股市相对债市有一定吸引力")
        elif erp_value > 0:
            print(f"    💡 ERP 在 0%-3% 之间，股市与债市吸引力接近")
        else:
            print(f"    ⚠️  ERP < 0%，债市收益率高于股市盈利收益率，股市偏贵")
        print(f"{'='*55}")

    # 综合信号分析 (三因子: 百分位 + CAPE偏离 + ERP)
    signal_label, signal_factors, signal_score, confidence = compute_composite_signal(
        percentile, cape_deviation, erp_value
    )
    print(f"\n  🎯 综合信号分析 (三因子模型):")
    print(f"    综合判定: {signal_label}  (评分: {signal_score:+d}, 置信度: {confidence})")
    print(f"    因子明细:")
    for f in signal_factors:
        print(f"      • {f}")
    print(f"{'='*55}")

    chart_path = generate_chart(df, current_pe, percentile, pe_percentile_values, erp_info)

    alert_triggered = False
    subject = ""
    body = ""

    # 构建补充分析文字 (邮件用)
    extra_analysis = ""
    if cape_deviation is not None:
        extra_analysis += (f"\n\n📏 CAPE偏离度: {cape_deviation:+.2f}%"
                          f" ({CAPE_ROLLING_YEARS}年均值PE: {cape_value:.2f})")
    if erp_info:
        ey, ev, byd = erp_info
        extra_analysis += (f"\n\n📊 股权风险溢价 (ERP): {ev*100:.2f}%"
                          f"\n  盈利收益率 (1/PE): {ey*100:.2f}%"
                          f"\n  10年期国债收益率:  {byd*100:.2f}%")
    extra_analysis += (f"\n\n🎯 综合信号: {signal_label} (评分: {signal_score:+d})")
    for f in signal_factors:
        extra_analysis += f"\n  • {f}"

    # 判断是否触发警报
    if percentile >= SELL_THRESHOLD:
        alert_triggered = True
        subject = f"🚨 {signal_label} | {INDEX_NAME} 估值过高 ({percentile:.1f}%)"
        body = (f"市场估值目前处于历史高位。\n"
                f"当前 PE TTM: {current_pe:.2f}\n"
                f"历史百分位: {percentile:.2f}%\n"
                f"建议策略：定投减速或开始分批减仓锁定利润。"
                f"{extra_analysis}")

    elif percentile <= BUY_THRESHOLD:
        alert_triggered = True
        subject = f"✅ {signal_label} | {INDEX_NAME} 估值低迷 ({percentile:.1f}%)"
        body = (f"市场估值目前处于历史底部区域。\n"
                f"当前 PE TTM: {current_pe:.2f}\n"
                f"历史百分位: {percentile:.2f}%\n"
                f"建议策略：适合加大定投筹码。"
                f"{extra_analysis}")

    if alert_triggered:
        print("\n满足预警条件，正在生成图表并发送邮件...")
        send_email_with_chart(subject, body, chart_path)
    else:
        print("\n当前估值处于正常区间，无需发送警报邮件。")

    # 生成供看板引用的 Markdown 报告
    save_markdown_report(current_pe, percentile, signal_label, signal_score, signal_factors, extra_analysis)

if __name__ == "__main__":
    main()