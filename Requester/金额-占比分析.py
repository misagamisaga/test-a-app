# import os
import pandas as pd
import numpy as np
import scipy
import math
# import proplot
import datetime

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")
# import plotly.figure_factory as ff

# 要有两个图，一个是散点/直方图，一个是饼图类的
# 先看一眼直方图，总体分布
# 然后给一个范围控件，控制大中小的百分比
# 然后处理一下数据
# 然后标注好贵/不贵的标签，然后画图

st.set_page_config(layout="centered")

#%% 按照时间重整数据

# 使用缓存来加速网页
@st.cache_data
def get_data():
    return pd.read_excel('bill_ok_proc.xlsx')

bill_ori = get_data()

fig_header_col1, fig_header_col2 = st.columns([3,2])
with fig_header_col1:
    st.header("金额-占比分析")
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

#%% 直方图
fig31_cho1, fig31_cho2 = st.columns(2)
with fig31_cho1:
    fig31_col11, fig31_col12 = st.columns([3,2])
    with fig31_col11:
        st.subheader("总体直方图")
    with fig31_col12:
        fig31_marginal = st.selectbox(
            "分布辅助显示", 
            (None, "box", "violin", "rug")
        )
        fig31_check0 = st.checkbox("仅支出", value=True)
        if fig31_check0:
            bill_fig31 = bill[bill["类型"] == "支出"]
        else:
            bill_fig31 = bill
    
with fig31_cho2:
    fig31_yuan = st.number_input(
        "直方图精细度 (元)", min_value=1, max_value=1000, value=5
    )
    fig31_numrange = st.slider(
        label="绘图范围", 
        min_value=0, max_value=math.ceil(bill_fig31['金额'].max()), 
        value=(0, math.ceil(bill_fig31['金额'].max()))
    )
    # st.write(fig31_numrange)
    bill_fig31_plot = bill_fig31[(bill_fig31['金额'] >= fig31_numrange[0]) & (bill_fig31['金额'] <= fig31_numrange[1])]

    
    fig31_nbins = math.ceil(bill_fig31_plot['金额'].max() / fig31_yuan)

fig31 = px.histogram(
    bill_fig31_plot, 
    x="金额",
    histfunc="count", 
    nbins=fig31_nbins,
    marginal=fig31_marginal
)
st.plotly_chart(fig31, use_container_width=True)

#%% 定义便宜-中-贵
st.markdown("##### 请在此定义便宜 - 一般 - 贵的价格范围, 然后进入后续分析")
temp_col1, temp_col2 = st.columns([1.3, 20])
with temp_col1:
    st.write("")
with temp_col2:
    mid_money = st.slider(
        label="None",
        label_visibility='hidden', 
        min_value=fig31_numrange[0], 
        max_value=fig31_numrange[1], 
        value = (
            int(fig31_numrange[0] + fig31_numrange[1] / 3), 
            math.ceil(fig31_numrange[0] + fig31_numrange[1] / 3 * 2)
        )
    )
st.markdown(
    "**当前价格定义:** \n 便宜: <"+str(mid_money[0])+
    "; 一般: "+str(mid_money[0])+"<=,<="+str(mid_money[1])+
    "; 贵: >"+str(mid_money[1])
)

# 打标签
# 将bill_fig31新增一列，其中“金额”列的值在mid_money范围内的标记为一般，更小的标记为便宜，更大的标记为贵
bill_fig31.loc[(bill_fig31['金额'] >= mid_money[0]) & (bill_fig31['金额'] <= mid_money[1]),"性质"] = "一般"
bill_fig31.loc[bill_fig31['金额'] > mid_money[1],"性质"] = "贵"
bill_fig31.loc[bill_fig31['金额'] < mid_money[0],"性质"] = "便宜"

#%% 正式绘图

st.markdown("---")
st.subheader("金额-占比分析")

#%% 控件

fig1_cho1, fig1_cho2 = st.columns(2)
with fig1_cho1:
    fig1_plot = st.selectbox(
        "选择图表类型",
        ("饼图", "柱状图", "箱型图", "小提琴图")
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
        
    if fig1_plot != "饼图":
        fig1_hv = st.checkbox("横向绘图", value=True)

def get_mode(x):
    return scipy.stats.mode(x)[0]
fig1_for0 = "性质"
#%% 数据二次处理

if fig1_plot in ["饼图", "柱状图"]:
    dict_proc = {"数量":"count", "总价":"sum", 
                "均价":"mean", "中位数":"median", 
                "众数":get_mode, "最大值":"max"}
    df_plot = bill_fig31.pivot_table(
        index=fig1_for0, values="金额", aggfunc=dict_proc[fig1_for1]
    ).reset_index(inplace=False).sort_values(by="金额", ascending=False).rename(columns={"性质":"性质", "金额":"值"}, inplace=False)

#%% 正式画图

# 得二次处理（透视表），且只能取前几个项目, 但是不用切片
if fig1_plot == "柱状图":
    if fig1_hv:
        fig2 = px.bar(df_plot, x='值', y=fig1_for0, orientation='h')
    else:
        fig2 = px.bar(df_plot, x=fig1_for0, y='值', orientation='v')
elif fig1_plot == "饼图":
    fig2 = px.pie(df_plot, values='值', names=fig1_for0)
    fig2.update_traces(
        textinfo='label+value+percent'
    )
elif fig1_plot == "箱型图":
    if fig1_hv:
        fig2 = px.box(bill_fig31, x="金额", y=fig1_for0, points=fig1_points, 
                      orientation='h', hover_data=['日期', '项目', '分类', '商家', '金额'])
    else:
        fig2 = px.box(bill_fig31, x=fig1_for0, y='金额', points=fig1_points, 
                      orientation='v', hover_data=['日期', '项目', '分类', '商家', '金额'])
    fig2.update_layout(template="ggplot2")
elif fig1_plot == "小提琴图":
    if fig1_hv:
        fig2 = px.violin(bill_fig31, x='金额', y=fig1_for0, points=fig1_points, 
                         orientation='h', hover_data=['日期', '项目', '分类', '商家', '金额'])
    else:
        fig2 = px.violin(bill_fig31, x=fig1_for0, y='金额', points=fig1_points, 
                         orientation='v', hover_data=['日期', '项目', '分类', '商家', '金额'])
    fig2.update_layout(template="ggplot2")
# fig2.update_layout(template="presentation")
st.plotly_chart(fig2, use_container_width=True)
