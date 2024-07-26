import os
import pandas as pd
import numpy as np
import proplot
import datetime
import math

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

#%% 按照时间重整数据

# 使用缓存来加速网页
@st.cache_data
def get_data():
    return pd.read_excel('bill_ok_proc.xlsx')

bill_ori = get_data()

fig_header_col1, fig_header_col2 = st.columns([3,2])
with fig_header_col1:
    st.header("时间-金额分析")
with fig_header_col2:
    date_choose = st.date_input(
        label = "选择分析日期",
        value = (
            datetime.date(2024, 6, 30), 
            datetime.date(2024, 7, 25)
        ),
        min_value = datetime.date(2024, 6, 30),
        max_value = datetime.date(2024, 7, 25),
        format="YYYY.MM.DD",
    )

# st.write(date_choose)

date_min_choose = pd.Timestamp(date_choose[0])
date_max_choose = pd.Timestamp(date_choose[1])

bill = bill_ori[(bill_ori['日期'] >= date_min_choose) & (bill_ori['日期'] <= date_max_choose)]
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
        ("折线图", "直方图", "散点图", "消费日历", "类别图")
    )
    
    fig1_for0 = st.selectbox(
        "选择查看项",
        ("总计", "项目", "分类", "商家")
    )
    
    if fig1_for0 != "总计":
        fig1_top_number = st.number_input(
            "显示条数",
            value=min(len(set(bill[fig1_for0].values)), 5),
            min_value=1,
            max_value=len(set(bill[fig1_for0].values)) 
        )

if fig1_for0 == "总计":
    fig1_for = None
    fig1_tuple_axis2 = ("余额", "金额", "累计金额")
else:
    fig1_for = fig1_for0
    fig1_tuple_axis2 = ("金额", fig1_for+"累计金额")


with fig1_cho2:
    fig1_axis2 = st.selectbox(
        "选择金额项",
        fig1_tuple_axis2
    )
    if fig1_plot == "直方图":
        fig31_marginal = st.selectbox(
            "分布辅助显示", 
            (None, "box", "violin", "rug")
        )
        n_days_all = bill["相对日"].max()
        bin_days = st.slider("分箱天数", min_value=1, max_value=n_days_all, value=7)
        fig31_nbins = math.ceil(n_days_all / bin_days)+1
    fig1cho2_cho1, fig1cho2_cho2 = st.columns([1,2])
    fig1cho2_cho3, fig1cho2_cho4 = st.columns(2)
    with fig1cho2_cho1:
        fig1_check0 = st.checkbox("仅支出", value=True)
    if fig1_for0 != "总计":
        with fig1cho2_cho2:
            fig1_check_num = st.checkbox("金额排序（否则按数量）", value=True)
        if fig1_plot == "折线图":
            with fig1cho2_cho3:
                fig1_check1 = st.checkbox("显示总余额")
                fig1_check2 = st.checkbox("显示总金额")
                fig1_check3 = st.checkbox("显示总累计金额")
            with fig1cho2_cho4:
                if fig1_check1 or fig1_check2 or fig1_check3:
                    fig1_check4 = st.checkbox("放缩显示", value=True)
                else:
                    fig1_check4 = False
    else:
        # fig1_check_num = False
        fig1_check1 = False
        fig1_check2 = False
        fig1_check3 = False
        fig1_check4 = False

#%% 数据二次处理

if fig1_check0:
    bill_fig1 = bill[bill["类型"] == "支出"]
else:
    bill_fig1 = bill
if fig1_for0 != "总计":
    if fig1_check_num:
        fig1_num_ref_index = bill_fig1.pivot_table(index=fig1_for, values="金额", aggfunc="sum").sort_values(by="金额", ascending=False).index.tolist()
    else:
        fig1_num_ref_index = bill_fig1[fig1_for].value_counts().index.tolist()
    
    bill_fig1_basic = bill_fig1[bill_fig1[fig1_for].isin(fig1_num_ref_index[:fig1_top_number])]
if fig1_plot == "折线图":
    if fig1_for0 != "总计":
        if fig1_check4:
            fig1_trans_rate1 = bill_fig1["金额"].max() / bill_fig1["余额"].max()
            fig1_trans_rate2 = bill_fig1["金额"].max() / bill_fig1["累计金额"].max()
            fig1_label_add = " (已放缩)"
        else:
            fig1_trans_rate1 = 1
            fig1_trans_rate2 = 1
            fig1_label_add = ""
    else:
        bill_fig1_basic = bill_fig1
        fig1_trans_rate1 = 1
        fig1_trans_rate2 = 1
        fig1_label_add = ""

#%% 正式画图
if fig1_plot == "折线图":
    if fig1_for0 == "总计":
        fig1 = px.line(bill_fig1_basic, x="日期", y=fig1_axis2)
    else:
        fig1 = px.line(bill_fig1_basic, x="日期", y=fig1_axis2, color=fig1_for)
    if fig1_check1:
        fig1.add_trace(
            go.Scatter(
                x=bill_fig1["日期"],
                y=bill_fig1["余额"] * fig1_trans_rate1,
                name="余额"+fig1_label_add,
                # mode="lines", 
                line=dict(
                    color="blue", 
                    width=3, 
                    dash="dot" # "dash"
                ), 
            )
        )
    if fig1_check2:
        fig1.add_trace(
            go.Scatter(
                x=bill_fig1["日期"],
                y=bill_fig1["金额"],
                name="金额",
                # mode="lines", 
                line=dict(
                    color="green", 
                    width=3, 
                    dash="dot" # "dash"
                ), 
            )
        )
    if fig1_check3:
        fig1.add_trace(
            go.Scatter(
                x=bill_fig1["日期"],
                y=bill_fig1["累计金额"] * fig1_trans_rate2,
                name="累计金额"+fig1_label_add,
                # mode="lines", 
                line=dict(
                    color="red", 
                    width=3, 
                    dash="dot" # "dash"
                ), 
            )
        )
    fig1.update_layout(template="ggplot2")
    st.plotly_chart(fig1, use_container_width=True)
elif fig1_plot == "直方图":
    fig1_hist = px.histogram(
        bill_fig1_basic,
        x="日期",
        y=fig1_axis2,
        color=fig1_for0,
        nbins=fig31_nbins, 
        marginal=fig31_marginal
    )
    fig1_hist.update_layout(template="seaborn")
    st.plotly_chart(fig1_hist, use_container_width=True)
