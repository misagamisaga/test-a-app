import pandas as pd
import streamlit as st
# import pickle
import os
import hashlib
import time
import yaml

def get_hashed_password(password_in, item_dict_in:dict):
    """
    salt: 加盐
    """
    true_salt = "secert_key_added%$^" + item_dict_in['role'] + item_dict_in['username'] + "and" + item_dict_in['true_name']
    hash_item = hashlib.sha3_256(true_salt.encode('utf-8'))
    hash_item.update(str(password_in).encode('utf-8'))
    hashed_password = hash_item.hexdigest()
    
    return hashed_password

if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

@st.fragment
def registr_part(users_info_input):
        
    st.markdown("---")
    # with st.form("Register form", border=False):
    user_name_res = st.text_input("用户名", key=123)
    true_name_res = st.text_input("真实姓名")
    user_mima_res1 = st.text_input("输入密码", type="password")
    user_mima_res2 = st.text_input("再次输入密码", type="password")
    email_res = st.text_input("E-mail")
    phone_number_res = st.text_input("电话号码")

    role_res_sel0 = st.selectbox("选择你的身份", ["一般用户", "管理员"])
    role_res_sel = "Admin" if role_res_sel0 == "管理员" else "Requester"

    if role_res_sel == "Admin":
        admin_auth_password_res = st.text_input("请输入管理员认证密码", type="password")

    button_res_col1, button_res_col2 = st.columns([1,6])
    # st.write(role_res_sel)
    with button_res_col1:
        submit_button4 = st.form_submit_button("确定注册")
        # submit_button4 = st.button("Register")
    with button_res_col2:
        submit_button5 = st.form_submit_button("取消")
        # submit_button5 = st.button("Cancel")

    if submit_button4:
        # register
        if len(user_name_res) == 0 or len(true_name_res) == 0 or len(user_mima_res1) == 0 or len(user_mima_res2) == 0 or len(email_res) == 0 or len(phone_number_res) == 0:
            st.error("请填写所有必填项")
        elif len(user_name_res) < 3:
            st.error("用户名长度必须大于等于3")
        elif len(user_mima_res1) < 6:
            st.error("密码长度必须大于等于6")
        elif user_name_res in users_info_input.keys():
            st.error("用户名已经存在")
        elif user_mima_res1 != user_mima_res2:
            st.error("两次输入的密码不一致")
        elif role_res_sel == "Admin" and admin_auth_password_res != "admin_auth_password":
            st.error("请输入正确的管理员密码")
        else:
            users_info_input[user_name_res] = {
                'username': user_name_res,
                'true_name': true_name_res,
                'role': role_res_sel,
                'password': str(user_mima_res1),
                'email': email_res,
                'phone_number': str(phone_number_res)
            }
            users_info_input[user_name_res]['password'] = get_hashed_password(
                users_info_input[user_name_res]['password'], users_info_input[user_name_res]
            )
            with open("users_info.yaml", "w", encoding="utf-8") as f:
                yaml.dump(users_info_input, stream=f, allow_unicode=True, sort_keys=False)
            
            st.success("注册成功")
            time.sleep(1)
            st.rerun()
    elif submit_button5:
        st.info("取消注册")
        time.sleep(0.1)
        st.rerun()

# 登陆页面
def login():
    st.set_page_config(layout="centered")
    st.header("欢迎使用月财务数据分析报表！")
    st.subheader("请登录")
    
    # role = st.selectbox("Choose your role", [None, "Requester", "Admin"])

    with st.form("Log in"):
        # if xxl_na == 1:
        with open("users_info.yaml", "r", encoding="utf-8") as f:
            users_info = yaml.load(f, Loader=yaml.FullLoader)
        # st.write(users_info)
        user_name = st.text_input("用户名")
        user_mima = st.text_input("密码", type="password")
        button_col1, button_col2, button_col3 = st.columns([1,7,1.2])
        with button_col1:
            submit_button1 = st.form_submit_button("登录")
        with button_col2:
            submit_button2 = st.form_submit_button("忘记密码")
        with button_col3:
            submit_button3 = st.form_submit_button("注册", use_container_width=True)
        
        if submit_button1:
            # log in
            if user_name not in users_info.keys():
                st.error("用户不存在，请注册")
            else:
                user_item = users_info[user_name]
                if (user_item is not None) and user_item['password'] == get_hashed_password(user_mima, user_item):
                    st.session_state.role = user_item['role']
                    st.session_state.username = user_item['username']
                    st.success("登陆成功")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
        elif submit_button2:
            st.info("请联系管理员重置密码")
        elif submit_button3:
            registr_part(users_info)
            

# 注销页面
def logout():
    st.session_state.role = None
    st.session_state.username = None
    st.rerun()

# 定义通用账户页面
logout_page = st.Page(
    logout, title="登出", icon=":material/logout:")
settings = st.Page(
    "settings.py", title="账号设置", icon=":material/settings:")

# 对每个具体的页面给一个定义函数
admin_1 = st.Page(
    "Admin/分析文件生成.py",
    title="分析文件生成",
    icon=":material/addchart:",  # 使用自带的Material icon shortcode来使用图标
    default=(st.session_state.role == "Admin"),  # 设置为该身份的默认页面
)
request_1 = st.Page(
    "Requester/时间-金额分析.py", 
    title="时间-金额分析", 
    icon=":material/timeline:", 
    default=(st.session_state.role == "Requester"),
)
request_2 = st.Page(
    "Requester/类别-金额分析.py",
    title="类别-金额分析",
    icon=":material/equalizer:",
)
request_3 = st.Page(
    "Requester/金额-占比分析.py", 
    title="金额-占比分析", 
    icon=":material/data_usage:",
)

# 将页面分组到列表中
account_pages = [logout_page, settings]
request_pages = [request_1, request_2, request_3]
admin_pages = [admin_1]

# 定义常见元素和导航, 这些内容会出现在所有页面中
# 额相当于加到了page_config里面
# st.title("Request manager")
# # 给一个徽标
# st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")

# 构建允许页面的字典
page_dict = {}
if st.session_state.role == "Admin":
    page_dict["中间数据生成"] = admin_pages
if st.session_state.role in ["Requester", "Admin"]:
    page_dict["分析"] = request_pages

# 如果被允许的页面不为空，则显示导航栏和被允许的访问的页面，否则显示登陆页面
if len(page_dict) > 0:
    pg = st.navigation({"账号": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()
