import pandas as pd 
import os
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')  # 屏蔽无关警告

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

df_analyzed_gap_gdp = pd.read_excel("city_finance_analysis\\data_clean\\analyzed_gap_gdp.xlsx")

# 2. 转换为目标格式：行=year，列=city，值=gap_to_gdp（可替换为你需要的指标）
df_pivot = df_analyzed_gap_gdp.pivot(index="year", columns="city", values="gap_to_gdp")

# 3. （可选）按年份降序排序，匹配你图中的2024→2019顺序
df_pivot = df_pivot.sort_index(ascending=True)

df_pivot.to_excel("city_finance_analysis\\data_clean\\analyzed_gap_gdp_pivot.xlsx")

df_房地产开发住宅投资额 = pd.read_excel("city_finance_analysis\\data_clean\\房地产开发住宅投资额.xlsx",index_col=0, header=0)
df_住宅商品房平均销售价格 = pd.read_excel("city_finance_analysis\\data_clean\\住宅商品房平均销售价格.xlsx",index_col=0, header=0)
df_住宅商品房平均销售面积 = pd.read_excel("city_finance_analysis\\data_clean\\住宅商品房平均销售面积.xlsx",index_col=0, header=0)
df_房地产开发住宅投资额 = df_房地产开发住宅投资额.sort_index(ascending=True)
df_住宅商品房平均销售价格 = df_住宅商品房平均销售价格.sort_index(ascending=True)
df_住宅商品房平均销售面积 = df_住宅商品房平均销售面积.sort_index(ascending=True)
df_住宅商品房销售总额 = df_住宅商品房平均销售价格 * df_住宅商品房平均销售面积 / 10000
df_住宅商品房销售总额.to_excel("city_finance_analysis\\data_clean\\住宅商品房销售总额.xlsx")

#
df_pivot["时间"] = df_pivot.index.astype(str)

# 1. 统一年份排序（升序）
common_years = df_pivot.index.intersection(df_住宅商品房销售总额.index)
common_cities = df_pivot.columns.intersection(df_住宅商品房销售总额.columns)

# 2. 筛选对齐后的数据（直接基于宽表操作）
gap = df_pivot.loc[common_years, common_cities]  # gap_to_gdp宽表
sales = df_住宅商品房销售总额.loc[common_years, common_cities]  # 销售总额宽表
invest = df_房地产开发住宅投资额.loc[common_years, common_cities]  # 投资额宽表
price = df_住宅商品房平均销售价格.loc[common_years, common_cities]  # 价格宽表
area = df_住宅商品房平均销售面积.loc[common_years, common_cities]  # 面积宽表

# 3. 计算房地产依赖度指标（宽表直接运算）
gdp = df_analyzed_gap_gdp.pivot(index="year", columns="city", values="gdp").loc[common_years, common_cities]
sales_to_gdp = sales / gdp  # 销售总额/GDP 宽表
invest_to_gdp = invest / gdp  # 投资额/GDP 宽表

print("="*60)
print("📊 房地产指标与gap_to_gdp 直接相关性分析（宽表运算）")
# 1. 整体相关性（按所有数据点计算）
total_corr_sales = gap.stack().corr(sales_to_gdp.stack())
total_corr_invest = gap.stack().corr(invest_to_gdp.stack())
total_corr_price = gap.stack().corr(price.stack())
total_corr_area = gap.stack().corr(area.stack())

print(f"销售总额/GDP 与 gap_to_gdp 相关系数: {total_corr_sales:.4f}")
print(f"开发投资额/GDP 与 gap_to_gdp 相关系数: {total_corr_invest:.4f}")
print(f"销售均价 与 gap_to_gdp 相关系数: {total_corr_price:.4f}")
print(f"销售面积 与 gap_to_gdp 相关系数: {total_corr_area:.4f}")

# 2. 分城市相关性（直接按列计算）
city_corr = pd.DataFrame({
    "sales_corr": [gap[city].corr(sales_to_gdp[city]) for city in common_cities],
    "invest_corr": [gap[city].corr(invest_to_gdp[city]) for city in common_cities],
    "price_corr": [gap[city].corr(price[city]) for city in common_cities],
    "area_corr": [gap[city].corr(area[city]) for city in common_cities]
}, index=common_cities)

print("\n📊 分城市相关性（前10个城市）:")
print(city_corr.head(10).round(4))
print("="*60)

# ==============================================
# 拉宽版：北上广深财政缺口率与房地产依赖度分图
# ==============================================
# 1. 数据准备（复用你已对齐的宽表）
target_cities = ["北京", "上海", "广州", "深圳"]
group1 = ["北京", "上海"]
group2 = ["广州", "深圳"]

# 统一数据格式：销售/GDP转为百分比
gap_plot = gap.loc[:, target_cities].copy()
sales_plot = sales_to_gdp.loc[:, target_cities].copy() * 100

# 专业配色与线型
colors = {"北京": "#1f77b4", "上海": "#ff7f0e", "广州": "#2ca02c", "深圳": "#d62728"}
line_styles = {"gap": "-", "sales": "--"}
markers = {"gap": "o", "sales": "s"}
sales_label = "房地产销售总额/GDP（%）"

# ==============================================
# 核心优化：拉宽画布（figsize从(18,8)改为(22,8)，宽度增加22%）
# ==============================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 8), sharey=True)
fig.suptitle("北上广深财政缺口率与房地产销售依赖度时序特征（2006-2024）", 
             fontsize=16, y=0.98)

# ==============================================
# 左图：北京+上海（拉宽后更舒展）
# ==============================================
# 左轴：财政缺口率
for city in group1:
    ax1.plot(gap_plot.index, gap_plot[city], 
             color=colors[city], linestyle=line_styles["gap"], 
             marker=markers["gap"], markersize=7, linewidth=2,
             label=f"{city} 财政缺口率")

# 右轴：房地产销售/GDP
ax1_twin = ax1.twinx()
for city in group1:
    ax1_twin.plot(sales_plot.index, sales_plot[city], 
                  color=colors[city], linestyle=line_styles["sales"], 
                  marker=markers["sales"], markersize=7, linewidth=2,
                  label=f"{city} {sales_label}")

# 坐标轴优化（保持曲线不超界）
ax1.set_xlabel("年份", fontsize=13, labelpad=12)
ax1.set_ylabel("财政缺口率（gap_to_gdp）", fontsize=13, color="#1f77b4", labelpad=12)
ax1.tick_params(axis="y", labelcolor="#1f77b4", labelsize=11)
ax1.grid(True, linestyle="--", alpha=0.7)
ax1.set_ylim(bottom=0, top=gap_plot[group1].max().max() * 1.05)
ax1.set_title("北京、上海 时序趋势", fontsize=14, pad=15)

ax1_twin.set_ylabel(sales_label, fontsize=13, color="#ff7f0e", labelpad=12)
ax1_twin.tick_params(axis="y", labelcolor="#ff7f0e", labelsize=11)
ax1_twin.set_ylim(bottom=0, top=sales_plot[group1].max().max() * 1.05)

# 图例（移到图外，不遮挡）
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, 
           loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize=11)

# ==============================================
# 右图：广州+深圳（拉宽后更舒展）
# ==============================================
# 左轴：财政缺口率
for city in group2:
    ax2.plot(gap_plot.index, gap_plot[city], 
             color=colors[city], linestyle=line_styles["gap"], 
             marker=markers["gap"], markersize=7, linewidth=2,
             label=f"{city} 财政缺口率")

# 右轴：房地产销售/GDP
ax2_twin = ax2.twinx()
for city in group2:
    ax2_twin.plot(sales_plot.index, sales_plot[city], 
                  color=colors[city], linestyle=line_styles["sales"], 
                  marker=markers["sales"], markersize=7, linewidth=2,
                  label=f"{city} {sales_label}")

# 坐标轴优化
ax2.set_xlabel("年份", fontsize=13, labelpad=12)
ax2.set_ylabel("财政缺口率（gap_to_gdp）", fontsize=13, color="#2ca02c", labelpad=12)
ax2.tick_params(axis="y", labelcolor="#2ca02c", labelsize=11)
ax2.grid(True, linestyle="--", alpha=0.7)
ax2.set_ylim(bottom=0, top=gap_plot[group2].max().max() * 1.05)
ax2.set_title("广州、深圳 时序趋势", fontsize=14, pad=15)

ax2_twin.set_ylabel(sales_label, fontsize=13, color="#d62728", labelpad=12)
ax2_twin.tick_params(axis="y", labelcolor="#d62728", labelsize=11)
ax2_twin.set_ylim(bottom=0, top=sales_plot[group2].max().max() * 1.05)

# 图例（移到图外，不遮挡）
lines3, labels3 = ax2.get_legend_handles_labels()
lines4, labels4 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines3 + lines4, labels3 + labels4, 
           loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize=11)

# ==============================================
# 布局优化（给图例留出空间，适配拉宽后的画布）
# ==============================================
plt.tight_layout(rect=[0, 0, 0.92, 0.95])
plt.savefig("city_finance_analysis\\output\\拉宽版_北上广深分图.png", 
            dpi=300, bbox_inches="tight")
plt.close()

print("✅ 图表拉宽完成！画布更舒展，曲线更清晰")


# ==============================================
# 地区差异分析（直接宽表分组计算）
# ==============================================
# 1. 城市分组定义
city_groups = {
    "一线城市": ["北京", "上海", "广州", "深圳"],
    "新一线城市": ["成都", "重庆", "杭州", "武汉", "西安", "苏州", "南京", "天津"],
    "二线城市": ["石家庄", "太原", "沈阳", "长春", "哈尔滨", "济南", "青岛"]
}

# 2. 直接按分组计算均值（宽表列筛选）
group_mean = {}
for group_name, cities in city_groups.items():
    group_cities = [city for city in cities if city in common_cities]
    if not group_cities:
        continue
    # 宽表直接取列计算均值
    group_mean[group_name] = {
        "gap_mean": gap[group_cities].mean(axis=1),  # 年度均值
        "sales_to_gdp_mean": sales_to_gdp[group_cities].mean(axis=1)
    }

# 3. 分组趋势可视化
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
colors_group = ["#1f77b4", "#ff7f0e", "#2ca02c"]

for i, (group_name, data) in enumerate(group_mean.items()):
    # 直接取宽表计算的均值序列绘图
    ax1.plot(data["gap_mean"].index, data["gap_mean"], marker="o", linewidth=2, color=colors_group[i], label=group_name)
    ax2.plot(data["sales_to_gdp_mean"].index, data["sales_to_gdp_mean"], marker="s", linewidth=2, color=colors_group[i], label=group_name)

ax1.set_xlabel("年份", fontsize=12)
ax1.set_ylabel("平均财政缺口率", fontsize=12)
ax1.set_title("分区域财政缺口率时序特征", fontsize=14)
ax1.grid(True, linestyle="--", alpha=0.7)
ax1.legend()

ax2.set_xlabel("年份", fontsize=12)
ax2.set_ylabel("平均房地产销售/GDP", fontsize=12)
ax2.set_title("分区域房地产依赖度时序特征", fontsize=14)
ax2.grid(True, linestyle="--", alpha=0.7)
ax2.legend()

plt.suptitle("分区域财政缺口率与房地产依赖度对比（宽表直接分析）", fontsize=16, y=1.02)
plt.tight_layout()
plt.savefig("city_finance_analysis\\output\\宽表_分区域趋势.png", dpi=300, bbox_inches="tight")
plt.close()

# ==============================================
# 五、结果导出（宽表直接保存）
# ==============================================
os.makedirs("city_finance_analysis\\output", exist_ok=True)
# 保存核心宽表
gap.to_excel("city_finance_analysis\\output\\宽表_gap_to_gdp.xlsx")
sales_to_gdp.to_excel("city_finance_analysis\\output\\宽表_销售依赖度.xlsx")
city_corr.to_excel("city_finance_analysis\\output\\宽表_分城市相关性.xlsx")

print("\n✅ 宽表直接分析完成！所有结果已保存至 output 文件夹")