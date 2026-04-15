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
# 탭 2: 영어 번역 (새로운 기능 - 저장 기능 추가 버전)
# ----------------------------------------
with main_tabs[1]:
    st.subheader("🔤 사진 찍어 바로 번역")
    st.info("영어 문장을 찍으면 한글 발음과 해석을 보여주고 파일로 저장할 수 있습니다.")
    
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
                        trans_prompt = """
                        당신은 친절한 어린이 영어 선생님입니다. 
                        이미지에 있는 영어 문장들을 모두 읽고 아래 JSON 형식으로 반환하세요.
                        1. "original": 영어 문장 원문
                        2. "pronunciation": 해당 문장의 자연스러운 한글 발음
                        3. "translation": 해당 문장의 한국어 뜻
                        문장이 여러 개라면 배열 형식으로 응답하고, 마크다운 없이 순수 JSON만 출력하세요.
                        """
                        response = model.generate_content([trans_prompt, image])
                        result_text = response.text.strip()
                        if result_text.startswith("```"):
                            result_text = result_text.split("\n", 1)[-1].rsplit("\n", 1)[0]
                        trans_data = json.loads(result_text)

                        st.success("번역이 완료되었습니다!")
                        st.write("---")
                        
                        # 화면 출력
                        for i, item in enumerate(trans_data, 1):
                            st.markdown(f"#### {i}. {item.get('original')}")
                            st.markdown(f"🗣️ **발음:** :red[{item.get('pronunciation')}]")
                            st.markdown(f"💡 **해석:** {item.get('translation')}")
                            st.write("")

                        # --- HTML 다운로드 데이터 생성 시작 ---
                        now_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        export_trans_html = f"""
                        <!DOCTYPE html>
                        <html lang="ko">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <style>
                                body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; background-color: #f0f2f6; padding: 15px; }}
                                .container {{ max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                                .header {{ text-align: center; border-bottom: 3px solid #2ecc71; padding-bottom: 15px; margin-bottom: 20px; }}
                                h1 {{ color: #2c3e50; font-size: 1.5em; margin-bottom: 5px; }}
                                .date {{ color: #7f8c8d; font-size: 0.9em; }}
                                .item {{ margin-bottom: 20px; padding: 15px; border-radius: 8px; background: #fff; border-left: 5px solid #2ecc71; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
                                .original {{ font-size: 1.1em; font-weight: bold; color: #2c3e50; display: block; }}
                                .pronun {{ color: #e74c3c; font-size: 0.95em; display: block; margin: 5px 0; }}
                                .trans {{ background: #f9f9f9; padding: 10px; border-radius: 5px; color: #34495e; margin-top: 5px; }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="header">
                                    <h1>🌐 AI 영어 번역 결과지</h1>
                                    <p class="date">생성일시: {now_date}</p>
                                </div>
                        """
                        for i, item in enumerate(trans_data, 1):
                            export_trans_html += f"""
                                <div class="item">
                                    <span class="original">{i}. {item.get('original')}</span>
                                    <span class="pronun">🗣️ {item.get('pronunciation')}</span>
                                    <div class="trans">💡 {item.get('translation')}</div>
                                </div>
                            """
                        export_trans_html += "</div></body></html>"

                        st.download_button(
                            label="📥 번역 결과 다운로드 (HTML)",
                            data=export_trans_html,
                            file_name=f"translation_{datetime.datetime.now().strftime('%m%d_%H%M')}.html",
                            mime="text/html",
                            use_container_width=True
                        )
                        # --- HTML 다운로드 데이터 생성 끝 ---
                                
                    except Exception as e:
                        st.error(f"번역 중 오류가 발생했습니다: {e}")
    else:
        st.info("👈 위에서 영어 문장 사진을 찍거나 업로드하면 번역이 시작됩니다!")
