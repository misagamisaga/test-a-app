import streamlit as st
import time
import yaml
import hashlib

def get_hashed_password(password_in, item_dict_in:dict):
    """
    salt: 加盐
    """
    true_salt = "secert_key_added%$^" + item_dict_in['role'] + item_dict_in['username'] + "and" + item_dict_in['true_name']
    hash_item = hashlib.sha3_256(true_salt.encode('utf-8'))
    hash_item.update(str(password_in).encode('utf-8'))
    hashed_password = hash_item.hexdigest()
    
    return hashed_password

st.header("修改用户信息")
with open("users_info.yaml", "r", encoding="utf-8") as f:
    users_info = yaml.load(f, Loader=yaml.FullLoader)

users_info_this = users_info[st.session_state['username']]

with st.form("setting"):
    st.markdown("#### 修改基本信息（在原有字段基础上修改即可）")
    user_name_res = st.text_input("用户名", value=users_info_this["username"])
    true_name_res = st.text_input("真实姓名", value=users_info_this["true_name"])
    email_res = st.text_input("E-mail", value=users_info_this["email"])
    phone_number_res = st.text_input("电话号码", value=users_info_this["phone_number"])

    st.markdown("---")
    st.markdown("#### 修改密码（留空则不修改）")
    user_mima_res1 = st.text_input("输入新密码", type="password")#, value=users_info_this["password"])
    user_mima_res2 = st.text_input("再次输入新密码", type="password")#, value=users_info_this["password"])
    st.markdown("---")

    st.markdown("#### 修改身份")
    role_res_sel0 = st.selectbox(
        "新的身份", ["一般用户", "管理员"], 
        index=0 if users_info_this["role"] == "Requester" else 1
    )

    role_res_sel = "Admin" if role_res_sel0 == "管理员" else "Requester"

    if role_res_sel == "Admin":
        admin_auth_password_res = st.text_input("请输入管理员认证密码", type="password")

    st.markdown("---")

    user_mima_res100 = st.text_input("请输入原来的密码以确认是您本人在操作", type="password")

    st.markdown("---")

    button_res_col1, button_res_col2 = st.columns([1,4])
    # st.write(role_res_sel)
    with button_res_col1:
        submit_button4 = st.form_submit_button("确定修改")
        # submit_button4 = st.button("Register")
    with button_res_col2:
        submit_button5 = st.form_submit_button("取消")
        # submit_button5 = st.button("Cancel")

    if submit_button4:
        if len(user_name_res) == 0 or len(true_name_res) == 0 or len(email_res) == 0 or len(phone_number_res) == 0:
            st.error("项目不可为空")
        elif get_hashed_password(user_mima_res100, users_info_this) != users_info_this['password']:
            st.error("请输入正确的原密码以确认是您本人在操作")
        elif user_mima_res1 != user_mima_res2:
            st.error("新输入的两个密码不一致")
        elif role_res_sel == "Admin" and admin_auth_password_res != "admin_auth_password":
            st.error("请输入正确的管理员密码")
        elif len(user_name_res) < 3:
            st.error("用户名长度必须大于等于3")
        elif len(user_mima_res1) < 6 and len(user_mima_res1) > 0:
            st.error("密码长度必须大于等于6")
        elif user_name_res in users_info.keys() and user_name_res != users_info_this['username']:
            st.error("用户名已经存在")
        else:
            if len(user_mima_res1) > 0:
                users_info[user_name_res] = {
                    'username': user_name_res,
                    'true_name': true_name_res,
                    'role': role_res_sel,
                    'password': str(user_mima_res1),
                    'email': email_res,
                    'phone_number': str(phone_number_res)
                }
                users_info[user_name_res]["password"] = get_hashed_password(
                    user_mima_res1, users_info[user_name_res]
                )
            else:
                users_info[user_name_res] = {
                    'username': user_name_res,
                    'true_name': true_name_res,
                    'role': role_res_sel,
                    'password': users_info_this['password'],
                    'email': email_res,
                    'phone_number': str(phone_number_res)
                }
            
            if user_name_res != users_info_this['username']:
                del users_info[users_info_this['username']]
            
            with open("users_info.yaml", "w", encoding="utf-8") as f:
                yaml.dump(users_info, stream=f, allow_unicode=True, sort_keys=False)
            
            st.success("修改成功")
            time.sleep(1)
            st.rerun()
    
    elif submit_button5:
        st.info("取消修改")
        time.sleep(0.1)
        st.rerun()