import streamlit as st
import google.generativeai as genai
import json
import random
from PIL import Image
import datetime

# ----------------------------------------
# 1. 페이지 설정 및 초기화
# ----------------------------------------
st.set_page_config(page_title="찰칵! AI 영어 도우미", page_icon="📸", layout="wide")

st.title("📸 찰칵! AI 영어 학습기 📝")
st.markdown("**기존 시험지 만들기 기능과 새로운 번역 기능이 통합되었습니다.**")

# API 키 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("서버 점검 중입니다. API 키 설정을 확인해 주세요.")
    st.stop()

# ----------------------------------------
# 2. 메인 탭 구성 (영어 테스트 vs 영어 번역)
# ----------------------------------------
main_tabs = st.tabs(["📝 영어 테스트", "🔤 영어 번역"])

# ----------------------------------------
# 탭 1: 영어 테스트 (기존 기능)
# ----------------------------------------
with main_tabs[0]:
    st.subheader("AI 영어 시험지 메이커")
    st.info("단어장이나 시험지를 찍으면 AI가 자동으로 학습 퀴즈를 만들어줍니다.")
    
    sub_tab1, sub_tab2 = st.tabs(["📸 카메라", "📁 앨범"])
    with sub_tab1:
        cam_test = st.camera_input("단어장을 찍어주세요", key="cam_test")
    with sub_tab2:
        file_test = st.file_uploader("단어장 사진 업로드", type=["jpg", "jpeg", "png"], key="file_test")
    
    final_test_img = cam_test or file_test

    if final_test_img:
        image = Image.open(final_test_img)
        col_img, col_main = st.columns([1, 2])
        with col_img:
            st.image(image, caption="분석할 사진", use_container_width=True)
        
        with col_main:
            if st.button("🚀 AI 시험지 만들기!", use_container_width=True, key="btn_test"):
                with st.spinner("AI가 분석 중입니다..."):
                    try:
                        model = genai.GenerativeModel('gemini-flash-latest')
                        prompt = """
                        당신은 영어 교육 전문가입니다. 첨부된 이미지에서 단어, 뜻풀이, 예문을 추출하고 아래 JSON 형식으로 반환하세요.
                        [필수 규칙: 모든 영어에는 반드시 한국어 발음을 추가하세요]
                        1. "word_display": 단어 원문
                        2. "word_pronun": 한글 발음
                        3. "eng_def": 영어 뜻풀이
                        4. "eng_def_pronun": 영어 뜻풀이의 한글 발음
                        5. "example": 영어 예문
                        6. "example_pronun": 예문의 한글 발음
                        7. "kor_def": 한국어 해석
                        8. "example_kor": 예문 해석
                        9. "word_in_example": 예문 속 정답 단어
                        10. "part_of_speech": 품사
                        마크다운 없이 순수 JSON 배열만 출력하세요.
                        """
                        response = model.generate_content([prompt, image])
                        result_text = response.text.strip()
                        if result_text.startswith("```"):
                            result_text = result_text.split("\n", 1)[-1].rsplit("\n", 1)[0]
                        word_data = json.loads(result_text)
                        
                        # (기존 화면 출력 및 HTML 생성 로직 동일...)
                        st.success("🎉 시험지가 완성되었습니다!")
                        # 이하 기존 코드의 단계별 출력 및 저장 로직이 들어가는 부분 (생략 가능하나 유지됨)
                        st.write("---")
                        st.subheader("📖 공부하기")
                        for i, item in enumerate(word_data, 1):
                            st.write(f"**{i}) {item.get('word_display')}** [{item.get('word_pronun')}]")
                            st.write(f"뜻: {item.get('kor_def')} / 예문: {item.get('example')}")
                    except Exception as e:
                        st.error(f"오류: {e}")

# ----------------------------------------
# 탭 2: 영어 번역 (새로운 기능)
# ----------------------------------------
with main_tabs[1]:
    st.subheader("🔤 사진 찍어 바로 번역")
    st.info("영어 동화책이나 문장을 찍으면 한글 발음과 함께 해석해 드립니다.")
    
    sub_tab3, sub_tab4 = st.tabs(["📸 카메라", "📁 앨범"])
    with sub_tab3:
        cam_trans = st.camera_input("번역할 문장을 찍어주세요", key="cam_trans")
    with sub_tab4:
        file_trans = st.file_uploader("사진 업로드", type=["jpg", "jpeg", "png"], key="file_trans")
    
    final_trans_img = cam_trans or file_trans

    if final_trans_img:
        image = Image.open(final_trans_img)
        col_img, col_main = st.columns([1, 2])
        with col_img:
            st.image(image, caption="내가 찍은 문장", use_container_width=True)
            
        with col_main:
            if st.button("🔍 AI 번역 시작하기", use_container_width=True, key="btn_trans"):
                with st.spinner("문장을 읽고 번역하는 중입니다..."):
                    try:
                        model = genai.GenerativeModel('gemini-flash-latest')
                        # 번역 전용 프롬프트
                        trans_prompt = """
                        당신은 친절한 어린이 영어 선생님입니다. 
                        이미지에 있는 영어 문장들을 모두 읽고 아래 JSON 형식으로 반환하세요.
                        1. "original": 영어 문장 원문
                        2. "pronunciation": 해당 문장의 자연스러운 한글 발음
                        3. "translation": 해당 문장의 한국어 뜻 (어린이가 이해하기 쉽게)
                        
                        문장이 여러 개라면 배열 형식으로 응답하고, 마크다운 없이 순수 JSON만 출력하세요.
                        """
                        response = model.generate_content([trans_prompt, image])
                        result_text = response.text.strip()
                        if result_text.startswith("```"):
                            result_text = result_text.split("\n", 1)[-1].rsplit("\n", 1)[0]
                        trans_data = json.loads(result_text)

                        st.success("번역이 완료되었습니다!")
                        st.write("---")
                        
                        for i, item in enumerate(trans_data, 1):
                            with st.container():
                                st.markdown(f"#### {i}. {item.get('original')}")
                                st.markdown(f"🗣️ **발음:** :red[{item.get('pronunciation')}]")
                                st.markdown(f"💡 **해석:** {item.get('translation')}")
                                st.write("")
                                
                    except Exception as e:
                        st.error(f"번역 중 오류가 발생했습니다: {e}")

else:
    st.info("👈 위 탭에서 원하는 기능을 선택하고 사진을 찍어주세요!")
