import pandas as pd
import streamlit as st


# 时间-金额分析: 折线图, 散点图, 消费日历，类别图【第几周，周几，小时】（加小的选项）, 
# 类别-金额分析（饼图、柱状图-(箱型图、扰动散点图、小提琴图+直方图)，笔数、总价、均价、中位数、众数、最大值）
# 金额占比分析（分布直方图、柱状图、大中小金额的饼图，可选按类别切片） - 还差点的标注

# 缺：增加鼠标悬浮显示
# 缺：main改成上传excel，修正格式，并自动生成处理后xlsx

# 缺：加入登录界面，and只有生成了之后才显示其它页面

@st.cache_data
def get_uploaded_data(file):
    data = pd.read_excel(file)
    return data

st.header("月账目分析报表")
st.write("""欢迎来到月账目分析报表！  
         在进行分析之前，**你需要先通过这个页面上传账目表，并生成分析用的中间文件**。  
         之后就可以通过左侧栏进入分析页面，尽情分析啦！""")
st.markdown("---")
st.write("""请在下方输入账目表。账目表要求:  
* 账目表应当为Excel格式, 内容在第一个Sheet"  
* 账目表的列应包含: `['类型', '金额', '项目', '分类', '商家', '日期']`六个项目  
其中`'日期'`应为日期格式, `'金额'`为带符号的数值 (支出为负), `'类型'`的值为`'收入'`或`'支出'`""")
uploaded_file = st.file_uploader("上传账目表", type=["xlsx"], accept_multiple_files=False)
col_pag1_1, col_pag1_2 = st.columns(2)
with col_pag1_1:
    time_ref0 = st.date_input("请输入起始日期")
    # st.write(pd.Timestamp(time_ref0))
with col_pag1_2:
    money_left = st.number_input("请输入当前余额", value=0.0, step=0.01)  # 目前剩余的钱

uploaded_ok = st.button("全部输入完成")

st.markdown("---")

if uploaded_ok:
    st.markdown("**这是你上传的数据, 请检查:**")
    bill = get_uploaded_data(uploaded_file)
    st.write(bill)

    time_ref = pd.Timestamp(time_ref0)  # 相对的起始日子

    bill = bill[bill['账户'] == '生活费']
    bill = bill[['类型', '金额', '项目', '分类', '商家', '日期']]
    bill = bill.fillna('其它', inplace=False)
    bill.columns = ['类型', '总金额', '项目', '分类', '商家', '日期']  # 总金额代表有符号方向的金额，金额改为绝对金额
    bill['金额'] = bill['总金额'].abs()
    bill.head()

    # 单独做出年、月、日、时、相对首日的日数这几个列
    week_dict = {0:"一", 1:"二", 2:"三", 3:"四", 4:"五", 5:"六", 6:"日"}
    def get_ymdh(time_stamp, time_ref):
        """
        输入单个时间戳，返回、年、月、日、时、相对首日日数
        ---
        输入
        - time_stamp: 单个时间戳
        - time_ref: 参考时间, 也是一个时间戳
        """
        year = time_stamp.year
        month = time_stamp.month
        day = time_stamp.day
        day_w = "星期"+week_dict[time_stamp.day_of_week]  # 0代表周一，6代表周日
        hour = time_stamp.hour
        week = time_stamp.week
        
        time_delta = time_stamp - time_ref
        day_delta = time_delta.days
        daymonth_delta = day + hour / 24 + time_stamp.minute / 1440
        dayweek_delta = time_stamp.day_of_week + hour / 24 + time_stamp.minute / 1440

        hour_delta = hour + time_stamp.minute/60
        return (year, month, week, day, 
                day_w, hour, day_delta, 
                hour_delta, daymonth_delta, dayweek_delta)


    (bill['年'], bill['月'], bill['周'], bill['日'], 
    bill['星期'], bill['时'], bill['相对日'], 
    bill['相对时'], bill["相对月内日"], bill['相对星期天']) = zip(*bill['日期'].apply(lambda x: get_ymdh(x, time_ref)))

    # 按时间排序
    bill = bill.sort_index(ascending=True)
    bill['temp_amont'] = - bill['总金额']
    bill['余额'] = [money_left] + (bill['temp_amont'].cumsum() + money_left).tolist()[:-1]
    bill.sort_index(ascending=False)
    bill = bill.drop(["temp_amont"], axis=1)
    bill.to_excel(r'F:\today\对账\bill_ok_proc.xlsx', index=False)

    st.header("恭喜！现在你可以进行后面的分析了")