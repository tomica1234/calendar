import streamlit as st
import csv
import datetime
import io
from icalendar import Calendar, Event
import pytz
import base64

st.title("レスカスケジュール")

# CSVファイルのアップロード
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")
jst = pytz.timezone('Asia/Tokyo')

if uploaded_file is not None:
    csv_content = uploaded_file.read().decode("utf-8-sig")
    csv_file = io.StringIO(csv_content)
    
    # CSV の区切り文字を自動判別
    try:
        sample = csv_file.read(1024)
        csv_file.seek(0)
        dialect = csv.Sniffer().sniff(sample)
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(csv_file, dialect=dialect)
    

    # iCal カレンダーの初期化
    cal = Calendar()
    cal.add("prodid", "-//My Calendar Product//example.com//")
    cal.add("version", "2.0")
    
    for row in reader:
        # ヘッダーのキーの余計な空白を除去
        row = {key.strip(): value for key, value in row.items()}
        try:
            date_str = row['日付']
            start_time_str = row['開始時間']
            end_time_str = row['終了時間']
            location = row['場所']
        except KeyError as e:
            st.error(f"CSVのヘッダーに必要なカラムが見つかりません: {e}")
            break

        # 日付と時刻を datetime オブジェクトに変換し、日本時間に設定
        start_dt = jst.localize(datetime.datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M"))
        end_dt = jst.localize(datetime.datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M"))
        
        event = Event()
        event.add("summary", f"レスカ@{location}")  # イベントのタイトルは必要に応じて変更
        event.add("dtstart", start_dt)
        event.add("dtend", end_dt)
        event.add("location", location)
        cal.add_component(event)
    
    # iCal のバイトデータを取得
    ical_bytes = cal.to_ical()
    
    # ① 通常のダウンロードボタン
    st.download_button(
        label="iCalファイルをダウンロード",
        data=ical_bytes,
        file_name="calendar.ics",
        mime="text/calendar"
    )
    
    # ② 共有用ダウンロードリンク（data URL）
    b64 = base64.b64encode(ical_bytes).decode('utf-8')
    data_url = f"data:text/calendar;base64,{b64}"
    st.markdown("### 共有用ダウンロードリンク")
    st.markdown(f"共有リンク{data_url}", unsafe_allow_html=True)
