import streamlit as st
import random

# 페이지 기본 설정
st.set_page_config(page_title="랜덤 자리 배치", layout="wide")

# 세션 상태 초기화: 데이터를 유지하기 위해 필요합니다.
if "seats" not in st.session_state:
    st.session_state.seats = ["(빈자리)"] * 22
if "remaining_names" not in st.session_state:
    st.session_state.remaining_names = []

# 왼쪽 사이드바 구성
st.sidebar.title("이름 명단 입력")
st.sidebar.write("총 22명의 이름을 줄바꿈으로 구분해서 입력해주세요.")
names_input = st.sidebar.text_area("명단", height=400)

if st.sidebar.button("명단 등록 및 초기화"):
    # 줄바꿈을 기준으로 이름을 나누고 공백을 제거합니다.
    names = [name.strip() for name in names_input.split('\n') if name.strip()]
    
    if len(names) == 22:
        st.session_state.remaining_names = names
        st.session_state.seats = ["(빈자리)"] * 22
        st.sidebar.success("22명의 명단이 성공적으로 등록되었습니다.")
    else:
        st.sidebar.error(f"현재 {len(names)}명이 입력되었습니다. 정확히 22명을 입력해야 합니다.")

# 메인 화면 구성
st.title("랜덤 자리 배치 프로그램")

# 한 명씩 자리를 배치하는 버튼
if st.button("1명 랜덤 배치하기"):
    if st.session_state.remaining_names:
        # 현재 빈자리의 인덱스 번호를 모두 찾습니다.
        empty_seat_indices = [i for i, seat in enumerate(st.session_state.seats) if seat == "(빈자리)"]
        
        if empty_seat_indices:
            # 남은 사람 중에서 무작위로 1명을 뽑습니다.
            person_index = random.randint(0, len(st.session_state.remaining_names) - 1)
            person = st.session_state.remaining_names.pop(person_index)
            
            # 남은 빈자리 중에서 무작위로 1개를 뽑습니다.
            seat_index = random.choice(empty_seat_indices)
            
            # 해당 자리에 뽑힌 사람의 이름을 넣습니다.
            st.session_state.seats[seat_index] = person
    else:
        st.warning("모든 인원이 자리에 배치되었습니다.")

st.write("---")

# 1행 출력 (6명, 2명씩 짝지어서 보여줍니다)
st.subheader("1행")
cols1 = st.columns(6)
for i in range(6):
    cols1[i].write(st.session_state.seats[i])

# 2행 출력 (8명)
st.subheader("2행")
cols2 = st.columns(8)
for i in range(8):
    cols2[i].write(st.session_state.seats[6 + i])

# 3행 출력 (8명)
st.subheader("3행")
cols3 = st.columns(8)
for i in range(8):
    cols3[i].write(st.session_state.seats[14 + i])
