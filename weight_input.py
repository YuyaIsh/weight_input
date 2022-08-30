import PySimpleGUI as sg
from datetime import datetime, timedelta
import psycopg2
import locale

locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')

location=(100,0)
popup_location = (location[0]+100,location[1]+200)

black = "#000000"
red = "#ff0000"
darkgray = "#696969"
gray = "#a9a9a9"
white = "#ffffff"

date_format = "%Y/%m/%d (%a)"

def main():
    sg.theme("Dark2")

    db = ConnectDB()


    # DBから読み出し
    data,colnames = db.select_weight()
    display_date = (datetime.strptime(data[0][0],date_format)+timedelta(days=1)).strftime(date_format)

#                       ##                                             ##
#                       ##                                             ##
#                       ##         ####  ##    ##   ####    ##    ##  ######
#                       ##        #   ##  #    ##  ##  ##   ##    ##   ##
#                       ##            ##  ##   #  ##    ##  ##    ##   ##
#                       ##           ###   #  ##  ##     #  ##    ##   ##
#                       ##        ######   ## #   #      #  ##    ##   ##
#                       ##       ##    #   ## #   ##     #  ##    ##   ##
#                       ##       ##   ##    ###   ##    ##  ##    ##   ##
#                       ##       ##  ###    ##     ##  ##    ##  ###   ##
#                       ########  #### #    ##      ####      ### ##   #####
#                                           #
#                                         ###
#                                         ##

    # 体重入力UI
    frame_weight = [
        [sg.T("体重入力"),sg.HorizontalSeparator()],
        [sg.Column([
            [sg.B("◀",key="pre_day",font=fontsize(13),pad=(0,10)),
             sg.Input(display_date,size=14,key="date",justification="center",pad=(0,10)),
             sg.B("▶",key="next_day",font=fontsize(13),pad=((0,10),0)),
             sg.B("TODAY",key="today",font=fontsize(13),pad=(0,0))],
            [sg.T("体重:",pad=(0,5)), sg.Input("",size=5,justification="right",key="weight",pad=0,focus=True),sg.T("kg",pad=0),
             sg.B("登録",key="input",pad=((15,0),0))]
        ],element_justification="center",justification="center")]
    ]

    # デイリーデータテーブル
    column_summary = sg.Column([
        [sg.T("デイリーデータ"),sg.HorizontalSeparator()],
        [sg.Table(data,headings=colnames,auto_size_columns=False,justification="center",col_widths=[14,7,7],key="table")]
    ])


    layout = [[sg.Text("Body manager",font=fontsize(22,True),pad=(2,(2,10)))],
        [frame_weight],
        [column_summary]
        ]


    window = sg.Window("Body Manager",layout,
                       location=location,
                       finalize=True,
                       font=fontsize(18))

    window["weight"].bind("<Return>","-return")

#                     #######
#                     ##    ##
#                     ##    ##
#                     ##     #
#                     ##    ##  ##  ##   ####      ####     ####    ####   ####
#                     ##   ###  ####    ##  ##    ##   ##  #   ##  ##  #  ##  #
#                     #######   ###    ##    ##  ##       #     #  ##     ##
#                     ##        ##     ##    ##  ##       #######   ##     ##
#                     ##        ##     ##    ##  ##       #           ##     ##
#                     ##        ##     ##    ##  ##       ##           ##     ##
#                     ##        ##      ##  ##    ##  ##   ##  ##  #   ## #   ##
#                     ##        ##       ####      ####     ####   #####  #####

    while True:
        event, values = window.read(timeout=100)

        if event == None:
            break

        if values["date"] == datetime.now().strftime(date_format):
            window["date"].update(text_color=black)
        else:
            window["date"].update(text_color=red)


#wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww 日付の処理 wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
        if "_day" in event:
            if "pre_" in event: delta = -1
            if "next_" in event: delta = 1

            date = datetime.strptime(values["date"],date_format)
            date = date + timedelta(days=delta)
            date = date.strftime(date_format)
            window["date"].update(value=date)

        if event == "today":
            date = datetime.now().strftime(date_format)
            window["date"].update(value=date)

#wwwwwwwwwwwwwwwwwwwwwwwwwwwww 体重を入力する処理 wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
        if event == "weight-return":
            window["input"].ButtonCallBack()

        if event == "input":
            date = datetime.strptime(values["date"],date_format)
            try:
                weight = "{:.2f}".format(float(values["weight"]))
            except:
                sg.PopupOK("入力値が不正です。",location=popup_location)
                continue
            try:
                try:
                    db.insert_weight(date,weight)
                except psycopg2.errors.UniqueViolation:
                    comfirm = sg.PopupOKCancel(f'{values["date"]}のデータは既に存在しています。\n更新しますか？',location=popup_location)
                    if comfirm == "OK":
                        db.update_weight(date,weight)
            except psycopg2.OperationalError:
                sg.PopupOK("サーバーに接続できません。",location=popup_location)
                continue

            date = datetime.strptime(values["date"],date_format)
            date = date + timedelta(days=1)
            date = date.strftime(date_format)
            window["date"].update(date)

            data,_ = db.select_weight()
            window["table"].update(data)


def fontsize(fontsize,bold=False):
    if not bold:
        return ("Meiryo UI",fontsize)
    else:
        return ("Meiryo UI",fontsize,"bold")


#                          ########        ########
#                          ###    ###      ###    ###
#                          ###      ###    ###    ###
#                          ###      ###    ########
#                          ###      ###    ###    ###
#                          ###    ###      ###    ###
#                          #######         ########



#dbdbdbdbdbdbdbdbdbdbdbdbdbdbdbdbdbdbd 体重テーブル dbdbdbdbdbdbdbdbdbdbdbdbdbdbdbdbdbdbdbdbddd
class ConnectDB:
    def __init__(self):
        ip = "107.22.122.106"
        port = 5432
        dbname = "ddlt9vnio30dl2"
        user = "toyfvzgwkwormw"
        pw = "c9b5ca00aa1952ec9d0ccbb5db706fb64c54bd4d0a14b45da6500b4e44802139"

        self.db_info = f"host={ip} port={port} dbname={dbname} user={user} password={pw}"

    def insert_weight(self,date,weight):
        sql = f"""
            INSERT INTO weight_log (date,yuya_weight)
            VALUES (\'{date}\',{weight})
            """
        with psycopg2.connect(self.db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()

    def update_weight(self,date,weight):
        sql = f"""
            update weight_log
            SET yuya_weight = {weight}
            WHERE date = \'{date}\'
            """
        with psycopg2.connect(self.db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()

    def select_weight(self):
        sql = f"""
            SELECT date,yuya_weight,yuya_moving_avg
            FROM weekly_weight_moving_avg
            ORDER BY date DESC limit 10
            """
        with psycopg2.connect(self.db_info) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                data = list(cur.fetchall())  # 一行1タプルとしてリスト化

        colnames = ["日付","体重","移動平均"]  # 列名をリストで取得
        for i in range(len(data)):
            data[i] = list(data[i])  # タプルをリストに変更
            data[i][0] = data[i][0].strftime(date_format)

        return data,colnames

try:
    main()
except psycopg2.OperationalError as e:
    window = sg.Window("Body Manager",[[sg.Text(f"サーバーに接続できません。\n{e}")]], location=location,finalize=True)
    while True:
        event,values = window.read()
        if event is None:
            break
