import streamlit as st
import psycopg2

def main():
    st.header("生活費計算","header")

    st.subheader("買ったもの","subheader")

    col_date,col_item,col_price,col_person = st.columns(4)
    with col_date:
        st.text("日付")
        st.input()
    with col_item:
        st.text("買ったもの")
        st.input()
    with col_price:
        st.text("価格")
        st.input()
    with col_person:
        st.text("払った人")
        st.radio()


    st.subheader(f"一覧 {month}月","subheader")
    st.dataframe(df)


    st.header(f"{person}が{total_price}円支払う","result")

class DB:
    def __init__():

    def insert(self):

    def select():
