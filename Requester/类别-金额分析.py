# import os
import pandas as pd
import numpy as np
import scipy
# import proplot
import datetime

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# 时间-金额分析: 折线图, 散点图, 消费日历，类别图【第几周，周几，小时】（加小的选项）, 
# 类别-金额分析（饼图、柱状图-(箱型图、扰动散点图、小提琴图)，笔数、总价、均价、中位数、众数、最大值）
# 金额占比分析（分布直方图、柱状图、大中小金额的饼图，可选按类别切片）

st.set_page_config(layout="centered")

#%% 按照时间重整数据

# 使用缓存来加速网页
@st.cache_data
def get_data():
    return pd.read_excel('bill_ok_proc.xlsx')

bill_ori = get_data()

fig_header_col1, fig_header_col2 = st.columns([3,2])
with fig_header_col1:
    st.header("类别-金额分析")
with fig_header_col2:
    date_choose = st.date_input(
        label = "选择分析日期",
        value = (
            bill_ori["日期"].min().date(), 
            bill_ori["日期"].max().date()
        ),
        min_value = bill_ori["日期"].min().date(), 
        max_value = bill_ori["日期"].max().date(), 
        format="YYYY.MM.DD",
    )

# st.write(date_choose)

date_min_choose = pd.Timestamp(date_choose[0])
date_max_choose = pd.Timestamp(date_choose[1]) + pd.Timedelta(days=1)

bill = bill_ori[(bill_ori['日期'] >= date_min_choose) & (bill_ori['日期'] < date_max_choose)]
bill.loc[:,"相对日"] = bill["相对日"] - bill["相对日"].min()
bill = bill.sort_values(by="日期", ascending=True)

for col in ['项目', '分类', '商家']:
    name_add_now = col + "累计金额"
    for item in set(bill[col].values):
        bool_sel = bill[col] == item
        cum_sel = bill[bool_sel]["金额"].cumsum()
        bill.loc[cum_sel.index, name_add_now] = cum_sel.values
col = "类型"
name_add_now = "累计金额"
for item in set(bill[col].values):
    bool_sel = bill[col] == item
    cum_sel = bill[bool_sel]["金额"].cumsum()
    bill.loc[cum_sel.index, name_add_now] = cum_sel.values

# st.dataframe(bill)

st.markdown("---")

#%% 控件

fig1_cho1, fig1_cho2 = st.columns(2)
with fig1_cho1:
    fig1_plot = st.selectbox(
        "选择图表类型",
        ("饼图", "柱状图", "箱型图", "小提琴图")
    )
    fig1_for0 = st.selectbox(
        "选择类目",
        ("项目", "分类", "商家")
    )
with fig1_cho2:
    if fig1_plot in ["饼图", "柱状图"]:
        fig1_for1 = st.selectbox(
            "选择数据类型",
            ("总价", "均价", "数量", "中位数", "众数", "最大值")
        )
    else:
        fig1_points = st.selectbox(
            "数据点显示",
            ("all", "outliers", False)
        )
        fig1_check_num = st.checkbox("金额排序（否则按数量）", value=True)
    fig1_check0 = st.checkbox("仅支出", value=True)
    
    if fig1_check0:
        bill_fig2 = bill[bill["类型"] == "支出"]
    else:
        bill_fig2 = bill
        
    if fig1_plot != "饼图":
        fig1_hv = st.checkbox("横向绘图", value=True)

with fig1_cho1:
    fig1_top_number = st.number_input(
        "显示条数",
        value=min(len(set(bill_fig2[fig1_for0].values)), 5),
        min_value=1,
        max_value=len(set(bill_fig2[fig1_for0].values)) 
    )
def get_mode(x):
    return scipy.stats.mode(x)[0]
#%% 数据二次处理

if fig1_plot in ["饼图", "柱状图"]:
    dict_proc = {"数量":"count", "总价":"sum", 
                "均价":"mean", "中位数":"median", 
                "众数":get_mode, "最大值":"max"}
    pix_df = bill_fig2.pivot_table(
        index=fig1_for0, values="金额", aggfunc=dict_proc[fig1_for1]
    ).reset_index(inplace=False).sort_values(by="金额", ascending=False)

    df_plot = pix_df[:fig1_top_number]
else:
    if fig1_check_num:
        fig1_num_ref_index = bill_fig2.pivot_table(index=fig1_for0, values="金额", aggfunc="sum").sort_values(by="金额", ascending=False).index.tolist()
    else:
        fig1_num_ref_index = bill_fig2[fig1_for0].value_counts().index.tolist()

    bill_fig2_basic = bill_fig2[bill_fig2[fig1_for0].isin(fig1_num_ref_index[:fig1_top_number])]

#%% 正式画图

# 得二次处理（透视表），且只能取前几个项目, 但是不用切片
if fig1_plot == "柱状图":
    if fig1_hv:
        fig2 = px.bar(df_plot, x='金额', y=fig1_for0, orientation='h')
    else:
        fig2 = px.bar(df_plot, x=fig1_for0, y='金额', orientation='v')
elif fig1_plot == "饼图":
    fig2 = px.pie(df_plot, values='金额', names=fig1_for0)
    fig2.update_traces(
        textinfo='label+value+percent'
    )
elif fig1_plot == "箱型图":
    if fig1_hv:
        fig2 = px.box(bill_fig2_basic, x="金额", y=fig1_for0, points=fig1_points, 
                      orientation='h', hover_data=['日期', '项目', '分类', '商家', '金额'])
    else:
        fig2 = px.box(bill_fig2_basic, x=fig1_for0, y='金额', points=fig1_points, 
                      orientation='v', hover_data=['日期', '项目', '分类', '商家', '金额'])
    fig2.update_layout(template="ggplot2")
elif fig1_plot == "小提琴图":
    if fig1_hv:
        fig2 = px.violin(bill_fig2_basic, x='金额', y=fig1_for0, points=fig1_points, 
                         orientation='h', hover_data=['日期', '项目', '分类', '商家', '金额'])
    else:
        fig2 = px.violin(bill_fig2_basic, x=fig1_for0, y='金额', points=fig1_points, 
                         orientation='v', hover_data=['日期', '项目', '分类', '商家', '金额'])
    fig2.update_layout(template="ggplot2")
# fig2.update_layout(template="presentation")
st.plotly_chart(fig2, use_container_width=True)
