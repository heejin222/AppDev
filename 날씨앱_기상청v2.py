from dotenv import load_dotenv 
import os  

import streamlit as st
import requests
import datetime
import json

# 👉 기상청 단기예보 API 기본 정보
load_dotenv() 
weather_key = os.getenv("WEATHER_KEY") or st.secrets["WEATHER_KEY"]
URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

# 👉 동네 이름 → 격자(nx, ny) 좌표 (일부 예시)
location_map = {
    "서울": (60, 127),
    "부산": (98, 76),
    "대구": (89, 90),
    "인천": (55, 124),
    "광주": (58, 74),
    "대전": (67, 100),
    "제주": (52, 38),
}

# 👉 현재 시각 기준 최신 base_time 계산
def get_base_time():
    now = datetime.datetime.now()
    minute = now.minute

    # 초단기실황은 매시 정각만 가능
    if minute < 40:
        now = now - datetime.timedelta(hours=1)
    base_time = now.strftime("%H00")
    base_date = now.strftime("%Y%m%d")
    return base_date, base_time

# 👉 Streamlit UI
st.title("🌦️ 실시간 동네 날씨 조회")

region = st.selectbox("지역을 선택하세요", list(location_map.keys()))

if st.button("날씨 가져오기"):
    nx, ny = location_map[region]
    base_date, base_time = get_base_time()

    params = {
        "serviceKey": weather_key,
        "pageNo": "1",
        "numOfRows": "1000",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny,
    }

    res = requests.get(URL, params=params)

    if res.status_code == 200:
        data = res.json()

        items = data['response']['body']['items']['item']

        weather = {}
        for item in items:
            category = item['category']
            value = item['obsrValue']
            weather[category] = value

        st.subheader(f"📍 {region} 날씨 ({base_date} {base_time} 기준)")
        st.write(f"🌡 기온(T1H): {weather.get('T1H', '-')}℃")
        st.write(f"💧 습도(REH): {weather.get('REH', '-')}%")
        st.write(f"🌧 강수형태(PTY): {weather.get('PTY', '-')} (0: 없음, 1: 비, 2: 비/눈, 3: 눈, 5: 빗방울, 6: 빗방울눈, 7: 눈날림)")
        st.write(f"💨 풍속(WSD): {weather.get('WSD', '-')} m/s")
    else:
        st.error("API 요청 실패 😢")
