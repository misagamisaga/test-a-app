import pandas as pd
import streamlit as st
import pickle
import os

import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
with open('auth.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# 使用现成的表单
name, authentication_status, username = authenticator.login(
    'main'
)  # "main"代表在主页面中

if authentication_status == None:
    st.warning(f"{name}, {username}请先登录")
elif not authentication_status:
    st.error(f"{name}, {username}用户名或密码错误")
else:
    st.success(f"{name}, {username}登录成功")

    authenticator.logout("Logout", "sidebar")  # 将注销按钮放在测栏顶上
    st.sidebar.title(f"welcome {name} as {username}")