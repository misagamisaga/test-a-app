import streamlit as st


# your-repository/
# ├── admin
# │   ├── admin_1.py
# │   └── admin_2.py
# ├── images
# │   ├── horizontal_blue.png
# │   └── icon_blue.png
# ├── request
# │   ├── request_1.py
# │   └── request_2.py
# ├── respond
# │   ├── respond_1.py
# │   └── respond_2.py
# ├── settings.py
# └── streamlit_app.py

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "Requester", "Admin"]  # None表示未登录状态

# 登陆页面
def login():

    st.header("Log in")
    role = st.selectbox("Choose your role", ROLES)

    if st.button("Log in"):
        st.session_state.role = role
        st.rerun()

# 注销页面
def logout():
    st.session_state.role = None
    st.rerun()

# 定义所有页面
role = st.session_state.role
# 定义账户页面
logout_page = st.Page(
    logout, title="Log out", icon=":material/logout:")
settings = st.Page(
    "settings.py", title="Settings", icon=":material/settings:")

# 对每个具体的页面给一个定义函数
admin_1 = st.Page(
    "Admin/分析文件生成.py",
    title="ADMIN 1",
    icon=":material/help:",  # 使用自带的icon图表
    default=(role == "Admin"),  # 设置为该身份的默认页面
)
request_1 = st.Page(
    "Requester/时间-金额分析.py", 
    title="Request 1", 
    icon=":material/bug_report:"
)
request_2 = st.Page(
    "Requester/类别-金额分析.py",
    title="Request 2",
    icon=":material/healing:",
    default=(role == "Responder"),
)
request_3 = st.Page(
    "Requester/金额-占比分析.py", 
    title="Request 3", 
    icon=":material/handyman:"
)

# 将页面分组到列表中
account_pages = [logout_page, settings]
request_pages = [request_1, request_2, request_3]
admin_pages = [admin_1]

# 定义常见元素和导航
st.title("Request manager")
# # 给一个徽标
# st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")

# 构建允许页面的字典
page_dict = {}
if st.session_state.role in ["Requester", "Admin"]:
    page_dict["Request"] = request_pages
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages

# 如果被允许的页面不为空，则显示导航栏和被允许的访问的页面，否则显示登陆页面
if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()
