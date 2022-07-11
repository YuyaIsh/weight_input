import streamlit as st
import psycopg2
import datetime
import pandas as pd

def main():
    db = ConnectDB()
    month = datetime.datetime.now().month
    persons = ["Y","M"]


    st.header("生活費計算","header")

    col_pre_month,col_current_month,a,a,a = st.columns(5)
    with col_pre_month:
        if st.button("前月を表示"):
            month = month -1
    with col_current_month:
        if st.button("今月を表示"):
            month = datetime.datetime.now().month


    # データ登録
    st.text("")
    st.subheader("買ったもの","subheader")

    col_date,col_item,col_price,col_person = st.columns(4)
    with col_date:
        date = st.date_input("日付")
    with col_item:
        bought_item = st.text_input("買ったもの")
    with col_price:
        price = st.text_input("価格")
    with col_person:
        paid_person = st.radio("払った人",persons,horizontal=True)

    if st.button("登録"):
        db.insert_data(date,bought_item,price,paid_person)


    # ログ確認&削除
    st.text("")
    st.subheader(f"{month}月一覧","subheader")

    df = db.select_data(month)
    col_df,col_delete = st.columns(2)
    with col_df:
        st.dataframe(df.iloc[::-1],height=300)

    with col_delete:
        with st.expander("データ削除フォーム"):
            id = st.number_input("削除するidを入力",df["id"].min(),df["id"].max(),value=df["id"].max())
            st.subheader(f"{df[df['id']==id].iat[0,2]}")
            if st.button("削除"):
                db.delete_data(id)


    df_sum = df[["値段","人"]].groupby("人").sum()  # 各自の合計金額を計算

    total_payment = {persons[x] : df_sum.at[persons[x],"値段"] for x in range(2)}  # 各自の合計金額を辞書化

    st.text("")
    st.subheader(f"{persons[0]}:{total_payment[persons[0]]} {persons[1]}:{total_payment[persons[1]]}")  #各自の合計金額

    calculated_price = abs(total_payment[persons[0]]-total_payment[persons[1]])  # 差額算出

    # 計算結果表示
    if total_payment[persons[0]] > total_payment[persons[1]]:
        st.header(f"{persons[1]}が{calculated_price}円支払う","result")
    elif total_payment[persons[0]] < total_payment[persons[1]]:
        st.header(f"{persons[0]}が{calculated_price}円支払う","result")
    else:
        st.header("支払額は同じ")

class ConnectDB:
    def __init__(self):
        ip = st.secrets["DB_IP"]
        port = st.secrets["DB_PORT"]
        dbname = "bodymake"
        user = st.secrets["DB_USER"]
        pw = st.secrets["DB_PW"]
        self.db_info = f"host={ip} port={port} dbname={dbname} user={user} password={pw}"

    def insert_data(self,date,bought_item,price,paid_person):
        sql = f"""
            INSERT INTO pay_log (pay_log_id,date,bought_items,price,person)
            VALUES (nextval(\'pay_log_id_seq\'),\'{date}\',\'{bought_item}\',{price},\'{paid_person}\')
            """
        with psycopg2.connect(self.db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()

    def select_data(self,month):
        sql = f"""
            SELECT * FROM pay_log
            where extract(month from date) = \'{month}\'
            """
        with psycopg2.connect(self.db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                data = list(cur.fetchall())  # 一行1タプルとしてリスト化

        colnames =["id","日付","買い物","値段","人"]
        df = pd.DataFrame(data,columns=colnames)  # データをデータフレーム化

        return df

    def delete_data(self,id):
        sql = f"""
            DELETE FROM pay_log
            WHERE pay_log_id = {id}
            """
        with psycopg2.connect(self.db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()

main()
