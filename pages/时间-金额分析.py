# import os
import pandas as pd
import numpy as np
# import proplot
import datetime
import math
import scipy

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

#%% 按照时间重整数据

# 类别图：以第几周、周几、小时为列类别


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
       
    if fig1_plot not in ["消费日历", "类别图"]:
        fig1_for0 = st.selectbox(
            "选择查看项",
            ("总计", "项目", "分类", "商家")
        )
        # 横轴选择
        if fig1_plot in ["直方图", "散点图"]:
            fig1_axisx0 = st.selectbox(
                "选择横轴",
                ("全视图", "月视图", "周视图", "日视图")
            )
            dict_axisx = {"全视图":"日期", "月视图":"相对月内日", "周视图":"相对星期天", "日视图":"相对时"}
            fig1_axisx = dict_axisx[fig1_axisx0]

        # 显示条数
        if fig1_for0 != "总计":
            fig1_top_number = st.number_input(
                "显示条数",             
                value=min(len(set(bill[fig1_for0].values)), 5),
                min_value=1,
                max_value=len(set(bill[fig1_for0].values)) 
            )
    else:  # 消费日历or类别图
        
        if fig1_plot == "消费日历":
            fig1_cal = st.selectbox(
                "选择分析类型",
                ("日 - 时", "日 (星期中) - 周", "日 (月中) - 月")
            )
            cal_choose = st.selectbox(
                "选择数据类型",
                ("总价", "均价", "数量", "中位数", "众数", "最大值")
            )
            fig1_for0 = "总计"
        else:
            fig14_plot = st.selectbox(
                "选择具体图表类型",
                ("饼图", "柱状图", "箱型图", "小提琴图")
            )
            fig1_cal = st.selectbox(
                "选择分析类型",
                ("日 - 时", "日 (星期中) - 周", "日 (月中) - 月")
            )
                

# 金额项选择, 预备fig1_cho2
if fig1_plot != "类别图":
    if fig1_for0 == "总计":
        fig1_for = None
        fig1_tuple_axis2 = ("余额", "金额", "累计金额")
    else:
        fig1_for = fig1_for0
        fig1_tuple_axis2 = ("金额", fig1_for+"累计金额")

with fig1_cho2:
    if fig1_plot != "类别图":
        fig1_axis2 = st.selectbox(
            "选择金额项",
            fig1_tuple_axis2
        )

    if fig1_plot == "类别图":
        if fig14_plot == "柱状图":
                fig1_for0 = st.selectbox(
                    "选择查看项",
                    ("总计", "项目", "分类", "商家")
                )
        else:
            fig1_for0 = None
        if fig14_plot in ["饼图", "柱状图"]:
            # fig1_for0 = st.selectbox(
            #     "选择查看项",
            #     ("总计", "项目", "分类", "商家")
            # )
            fig14_for1 = st.selectbox(
                "选择数据类型",
                ("总价", "均价", "数量", "中位数", "众数", "最大值"), 
                # key=1001
            )
        else:
            fig14_points = st.selectbox(
                "数据点显示",
                ("all", "outliers", False)
            )
            # fig14_check_num = st.checkbox("金额排序（否则按数量）", value=True)
    else:
        fig14_plot = None    

    # 仅直方图: 辅助显示的箱型图, 直方图的显示范围
    if fig1_plot == "直方图":
        fig31_marginal0 = st.selectbox(
            "分布辅助显示", 
            ("无", "箱型图", "小提琴图", "线图")
        )
        dict_marginal = {
            "无":None, 
            "箱型图":"box", 
            "小提琴图":"violin", 
            "线图":"rug"
        }
        fig31_marginal = dict_marginal[fig31_marginal0]

        bindaysname_dict = {
            "全视图":("分箱大小 (日）", bill["相对日"].max(), 2), 
            "月视图":("分箱大小 (月内天数)", 30, 2),
            "周视图":("分箱大小 (星期内天数)", 7, 1),
            "日视图":("分箱大小 (小时)", 24, 2)
        }
        bin_days_name, n_days_all, bin_defalut = bindaysname_dict[fig1_axisx0]
        bin_days = st.slider(bin_days_name, min_value=1, max_value=n_days_all, value=bin_defalut)
        fig31_nbins = math.ceil(n_days_all / bin_days)+1
    
    fig1cho2_cho1, fig1cho2_cho2 = st.columns([1,2])
    fig1cho2_cho3, fig1cho2_cho4 = st.columns(2)
    with fig1cho2_cho1:
        fig1_check0 = st.checkbox("仅支出", value=True)
    if fig1_plot != "消费日历":
        if fig1_for0 != "总计":
            if fig1_plot != "类别图":
                with fig1cho2_cho2:
                    fig1_check_num = st.checkbox("金额排序（否则按数量）", value=True)
            # 仅折线图且不为总计: 是否显示总的折线, 是否放缩显示
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
        with fig1cho2_cho2:
            if fig14_plot in ["柱状图", "箱型图", "小提琴图"]:
                fig14_hv = st.checkbox("横向绘图", value=False)


#%% 数据二次处理

# 仅支出
if fig1_check0:
    bill_fig1 = bill[bill["类型"] == "支出"]
else:
    bill_fig1 = bill

def get_mode(x):
    return scipy.stats.mode(x)[0]
dict_calender = {
    "日 - 时":"时", 
    "日 (星期中) - 周":"星期", 
    "日 (月中) - 月":"日"
}

if fig1_plot == "类别图":
    calender_input = dict_calender[fig1_cal]

if fig14_plot == "饼图":
    dict_proc = {"数量":"count", "总价":"sum", 
                "均价":"mean", "中位数":"median", 
                "众数":get_mode, "最大值":"max"}
    # bill_fig1_pivot_temp = bill_fig1.copy()
    # bill_fig1_pivot_temp.loc[:,"总计"] = "总计"
    # calender_input = dict_calender[fig1_cal]
    df_plot = bill_fig1.pivot_table(
        index=calender_input, values="金额", aggfunc=dict_proc[fig14_for1]
    ).reset_index(inplace=False).sort_values(by="金额", ascending=False)
elif fig14_plot == "柱状图":
    # fig1_for0, ("总计", "项目", "分类", "商家")
    dict_proc = {"数量":"count", "总价":"sum", 
                "均价":"mean", "中位数":"median", 
                "众数":get_mode, "最大值":"max"}
    # bill_fig1_pivot_temp = bill_fig1.copy()
    # bill_fig1_pivot_temp.loc[:,"总计"] = "总计"
    # calender_input = dict_calender[fig1_cal]
    if fig1_for0 == "总计":
        df_plot = bill_fig1.pivot_table(
            index=calender_input, values="金额", aggfunc=dict_proc[fig14_for1]
        ).reset_index(inplace=False)
    else:
        df_plot000 = bill_fig1.pivot_table(
            index=calender_input, columns=fig1_for0, values="金额", aggfunc=dict_proc[fig14_for1]
        ).fillna(0)
        added_cols = df_plot000.columns.tolist()
        df_plot = df_plot000.reset_index(inplace=False)
# 只保留前几条
if fig1_plot != "类别图":
    if fig1_for0 != "总计":
        if fig1_check_num:
            fig1_num_ref_index = bill_fig1.pivot_table(index=fig1_for, values="金额", aggfunc="sum").sort_values(by="金额", ascending=False).index.tolist()
        else:
            fig1_num_ref_index = bill_fig1[fig1_for].value_counts().index.tolist()
        
        bill_fig1_basic = bill_fig1[bill_fig1[fig1_for].isin(fig1_num_ref_index[:fig1_top_number])]
    else:
        bill_fig1_basic = bill_fig1

# 折线图放缩功能
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
        x=fig1_axisx,
        y=fig1_axis2,
        color=fig1_for,
        nbins=fig31_nbins, 
        marginal=fig31_marginal
    )
    fig1_hist.update_layout(template="ggplot2")
    st.plotly_chart(fig1_hist, use_container_width=True)
elif fig1_plot == "散点图":
    fig1_hist = px.scatter(
        bill_fig1_basic,
        x=fig1_axisx,
        y=fig1_axis2,
        color=fig1_for,
    )
    fig1_hist.update_layout(template="ggplot2")
    st.plotly_chart(fig1_hist, use_container_width=True)
elif fig1_plot == "消费日历":
    dict_calender = {
        "日 - 时":("时", "相对日"), 
        "日 (星期中) - 周":("星期", "周"), 
        "日 (月中) - 月":("日", "月")
    }
    calender_input = dict_calender[fig1_cal]
    def get_mode(x):
        return scipy.stats.mode(x)[0]
    dict_proc = {"数量":"count", "总价":"sum", 
                "均价":"mean", "中位数":"median", 
                "众数":get_mode, "最大值":"max"}

    calender_df = bill_fig1_basic.pivot_table(
        values='金额', index=calender_input[1], 
        columns=calender_input[0], aggfunc=dict_proc[cal_choose]
    ).fillna(0)
    fig1_heatmap = px.imshow(
        calender_df
    )
    fig1_heatmap.update_xaxes(side="top")
    fig1_heatmap.update_layout(template="ggplot2")
    st.plotly_chart(fig1_heatmap, use_container_width=True)
elif fig1_plot == "类别图":
    if fig14_plot == "柱状图":
        # fig1_for0
        if fig1_for0 == "总计":
            if fig14_hv:
                fig2 = px.bar(df_plot, x="金额", y=calender_input, orientation='h')
            else:
                fig2 = px.bar(df_plot, x=calender_input, y="金额", orientation='v')
        else:
            if fig14_hv:
                fig2 = px.bar(df_plot, x=added_cols, y=calender_input, orientation='h')
            else:
                fig2 = px.bar(df_plot, x=calender_input, y=added_cols, orientation='v')
    elif fig14_plot == "饼图":
        fig2 = px.pie(df_plot, values="金额", names=calender_input)
    elif fig14_plot == "箱型图":
        if fig14_hv:
            fig2 = px.box(bill_fig1, x="金额", y=calender_input, points=fig14_points, 
                          orientation='h', hover_data=['日期', '项目', '分类', '商家', '金额'])
        else:
            fig2 = px.box(bill_fig1, x=calender_input, y="金额", points=fig14_points, 
                          orientation='v', hover_data=['日期', '项目', '分类', '商家', '金额'])
        fig2.update_layout(template="ggplot2")
    elif fig14_plot == "小提琴图":
        if fig14_hv:
            fig2 = px.violin(bill_fig1, x="金额", y=calender_input, points=fig14_points, 
                             orientation='h', hover_data=['日期', '项目', '分类', '商家', '金额'])
        else:
            fig2 = px.violin(bill_fig1, x=calender_input, y="金额", points=fig14_points, 
                             orientation='v', hover_data=['日期', '项目', '分类', '商家', '金额'])
        fig2.update_layout(template="ggplot2")
    # fig2.update_layout(template="presentation")
    st.plotly_chart(fig2, use_container_width=True)
