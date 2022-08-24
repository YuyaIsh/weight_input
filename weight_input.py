import streamlit as st
import psycopg2
import datetime
import pandas as pd
import plotly.graph_objects as go


persons = ["雄也","枚"]

def main():
    db = ConnectDB()
    month = datetime.datetime.now().month
    df = db.select_data()

    st.subheader("体重管理")

    tab_input, tab_graph = st.tabs(["入力", "グラフ"])

    # データ登録
    with tab_input:
        col_date,col_weight,col_person = st.columns(3)
        with col_date:
            date = st.date_input("日付")
        with col_weight:
            weight = st.text_input("体重")
        with col_person:
            person = st.radio("",persons,horizontal=True)

        if st.button("登録"):
            if weight == "":
                st.warning("価格を入力してください。")
            else:
                try:
                    db.update_data(date,weight,person)
                except:
                    pass
                st.success("データ登録に成功しました。")
                st.experimental_rerun()

    st.dataframe(df,height=500)


    # 結果表示
    with tab_graph:
        fig = go.Figure(data=[
                go.Scatter(x=df["date"],y=df["yuya_weight"]),
                go.Scatter(x=df["date"],y=df["yuya_weight_avg"]),
                go.Scatter(x=df["date"],y=df["mai_weight"]),
                go.Scatter(x=df["date"],y=df["mai_weight_avg"])
            ])
        fig.update_layout(height=800,
                        width=1500,
                        margin={'l': 20, 'r': 60, 't': 30, 'b': 0})

        st.plotly_chart(fig)

class ConnectDB:
    def __init__(self):
        ip = st.secrets["host"]
        port = st.secrets["port"]
        dbname = st.secrets["dbname"]
        user = st.secrets["user"]
        pw = st.secrets["password"]


        self.db_info = f"host={ip} port={port} dbname={dbname} user={user} password={pw}"

    def update_data(self,date,weight,person):
        if person == persons[0]: person = "yuya"
        elif person == persons[1]: person = "mai"
        sql = f"""
            INSERT INTO weight_log (date,{person}_weight)
            VALUES (\'{date}\',{weight})
            on conflict (date)
            do update set
                date=excluded.date,
                {person}_weight=excluded.{person}_weight
            """
        with psycopg2.connect(self.db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()

    def select_data(self):
        sql = f"""
            SELECT * FROM weekly_weight_moving_avg
            ORDER BY date DESC
            """
        with psycopg2.connect(self.db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                data = list(cur.fetchall())  # 一行1タプルとしてリスト化
                colnames = [col.name for col in cur.description]  # 列名をリストで取得
        df = pd.DataFrame(data,columns=colnames)  # データをデータフレーム化

        return df


main()