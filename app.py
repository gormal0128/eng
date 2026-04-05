import streamlit as st
import google.generativeai as genai
import json
import random
from PIL import Image
import datetime  # 날짜 추가를 위해 필요

# ----------------------------------------
# 1. 페이지 설정 및 초기화
# ----------------------------------------
st.set_page_config(page_title="찰칵! AI 영어 단어장", page_icon="📸", layout="wide")

st.title("📸 찰칵! AI 영어 시험지 메이커 📝")
st.markdown("**모바일 최적화 HTML 저장 기능이 적용된 대국민용 버전입니다.**")
st.markdown("---")

# Streamlit 서버의 비밀 금고에서 API 키 불러오기
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("서버 점검 중입니다. API 키 설정을 확인해 주세요.")
    st.stop()

# ----------------------------------------
# 2. 메인 로직 (이미지 업로드 및 촬영)
# ----------------------------------------
tab1, tab2 = st.tabs(["📸 카메라로 바로 찍기", "📁 앨범에서 사진 고르기"])

with tab1:
    camera_photo = st.camera_input("카메라 권한을 허용하고 단어장을 찰칵! 찍어주세요")

with tab2:
    uploaded_file = st.file_uploader("단어장 사진을 올려주세요 (JPG, PNG)", type=["jpg", "jpeg", "png"])

final_image = camera_photo or uploaded_file

if final_image is not None:
    image = Image.open(final_image)
    
    col_img, col_main = st.columns([1, 2])
    with col_img:
        st.image(image, caption="내가 올린 사진", use_container_width=True)
        
    with col_main:
        st.info("사진 분석 준비 완료! 버튼을 눌러주세요.")
        if st.button("🚀 AI 시험지 만들기!", use_container_width=True):
            with st.spinner("AI가 분석 중입니다... (약 15~20초 소요)"):
                try:
                    model = genai.GenerativeModel('gemini-flash-latest')

                    prompt = """
                    당신은 영어 교육 전문가입니다. 첨부된 이미지에서 단어, 뜻풀이, 예문을 추출하고 아래 JSON 형식으로 반환하세요.
                    
                    [필수 규칙: 모든 영어에는 반드시 한국어 발음을 추가하세요]
                    1. "word_display": 사진 속 단어 원문 (예: press - pressed)
                    2. "word_pronun": "word_display"의 한글 발음
                    3. "eng_def": 영어 뜻풀이 원문
                    4. "eng_def_pronun": "eng_def" 전체 문장의 한글 발음
                    5. "example": 영어 예문 원문
                    6. "example_pronun": "example" 전체 문장의 한글 발음
                    7. "kor_def": 뜻풀이의 한국어 해석
                    8. "example_kor": 예문의 한국어 해석
                    9. "word_in_example": 예문 속 정답 단어
                    10. "part_of_speech": 품사 기호 (v, n, adj 등)

                    마크다운 없이 순수 JSON 배열만 출력하세요.
                    """

                    response = model.generate_content([prompt, image])
                    result_text = response.text.strip()
                    if result_text.startswith("```"):
                        result_text = result_text.split("\n", 1)[-1].rsplit("\n", 1)[0]
                    word_data = json.loads(result_text)

                    if isinstance(word_data, dict):
                        for key in word_data:
                            if isinstance(word_data[key], list):
                                word_data = word_data[key]
                                break

                    st.success("🎉 시험지가 완성되었습니다!")
                    
                    # ----------------------------------------
                    # 3. 화면 출력
                    # ----------------------------------------
                    st.markdown("---")
                    st.subheader("📖 1단계: 공부하기")
                    for i, item in enumerate(word_data, 1):
                        pos = f"{item.get('part_of_speech', '')} " if item.get('part_of_speech') else ""
                        word_display = item.get('word_display', 'N/A')
                        word_pron = f"[{item.get('word_pronun', '')}]"
                        eng_def = item.get('eng_def', '')
                        eng_def_pron = f"[{item.get('eng_def_pronun', '')}]"
                        kor_def = item.get('kor_def', '')
                        example = item.get('example', '')
                        example_pron = f"[{item.get('example_pronun', '')}]"
                        example_kor = item.get('example_kor', '')

                        st.markdown(f"**{i}) {pos}{word_display} {word_pron}**")
                        st.write(f"  🇺🇸 **뜻:** {eng_def} [{item.get('eng_def_pronun', '')}]  \n  🇰🇷 **해석:** {kor_def}")
                        st.write(f"  📝 **예문:** {example} [{item.get('example_pronun', '')}]  \n  🇰🇷 **해석:** {example_kor}")
                        st.write("")

                    st.markdown("---")
                    st.subheader("🎯 2단계: 뜻 보고 단어 쓰기")
                    quiz2 = word_data.copy()
                    random.shuffle(quiz2)
                    for i, item in enumerate(quiz2, 1):
                        st.write(f"**{i})** {item.get('eng_def', '')} [{item.get('eng_def_pronun', '')}]")
                    
                    st.markdown("---")
                    st.subheader("🎯 3단계: 예문 빈칸 채우기")
                    quiz3 = word_data.copy()
                    random.shuffle(quiz3)
                    for i, item in enumerate(quiz3, 1):
                        target = item.get('word_in_example', '')
                        ex_text = item.get('example', '')
                        # 💡 [수정] 화면 출력 시 한글 발음 제거
                        if target:
                            blanked = ex_text.replace(target, "______").replace(target.capitalize(), "______")
                            st.write(f"**{i})** {blanked}")
                        else:
                            st.write(f"**{i})** {ex_text}")

                    # ----------------------------------------
                    # 4. HTML 데이터 생성 (날짜 추가 & 3단계 발음 제거)
                    # ----------------------------------------
                    st.markdown("---")
                    st.subheader("💾 시험지 저장하기")
                    
                    # 현재 날짜 가져오기
                    now_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                    export_html = f"""
                    <!DOCTYPE html>
                    <html lang="ko">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f9; padding: 15px; }}
                            .container {{ max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                            .header {{ text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 15px; margin-bottom: 20px; }}
                            h1 {{ color: #2c3e50; font-size: 1.5em; margin-bottom: 5px; }}
                            .date {{ color: #7f8c8d; font-size: 0.9em; }}
                            h2 {{ color: #e67e22; border-left: 5px solid #e67e22; padding-left: 10px; margin-top: 30px; font-size: 1.2em; }}
                            .item {{ margin-bottom: 20px; padding: 10px; border-bottom: 1px solid #eee; }}
                            .word {{ font-size: 1.1em; font-weight: bold; color: #2980b9; }}
                            .pronun {{ color: #e74c3c; font-size: 0.9em; }}
                            .eng {{ color: #2c3e50; font-weight: bold; display: block; margin-top: 5px; }}
                            .kor {{ color: #7f8c8d; font-size: 0.9em; display: block; }}
                            .box {{ background: #f9f9f9; padding: 10px; border-radius: 5px; margin-top: 10px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h1>📝 AI 영어 단어 시험지</h1>
                                <p class="date">생성일시: {now_date}</p>
                            </div>

                            <h2>1단계: 공부하기</h2>
                    """
                    for i, item in enumerate(word_data, 1):
                        export_html += f"""
                        <div class="item">
                            <span class="word">{i}) {item.get('part_of_speech', '')} {item.get('word_display')}</span> 
                            <span class="pronun">[{item.get('word_pronun')}]</span>
                            <div class="box">
                                <span class="eng">뜻: {item.get('eng_def')} <small class="pronun">[{item.get('eng_def_pronun')}]</small></span>
                                <span class="kor">해석: {item.get('kor_def')}</span>
                            </div>
                            <div class="box" style="background:#fffbe6;">
                                <span class="eng">예문: {item.get('example')} <small class="pronun">[{item.get('example_pronun')}]</small></span>
                                <span class="kor">해석: {item.get('example_kor')}</span>
                            </div>
                        </div>
                        """
                    
                    export_html += "<h2>2단계: 뜻 보고 단어 쓰기</h2>"
                    for i, item in enumerate(quiz2, 1):
                        export_html += f"<div class='item'>{i}) {item.get('eng_def')} <br><small class='pronun'>[{item.get('eng_def_pronun')}]</small></div>"
                    
                    export_html += "<h2>3단계: 예문 빈칸 채우기</h2>"
                    for i, item in enumerate(quiz3, 1):
                        target = item.get('word_in_example', '')
                        ex_text = item.get('example', '')
                        # 💡 [수정] HTML 문서에서도 3단계 한글 발음 제거
                        blanked = ex_text.replace(target, "______").replace(target.capitalize(), "______") if target else ex_text
                        export_html += f"<div class='item'>{i}) {blanked}</div>"

                    # 정답지 섹션 추가
                    export_html += """
                    <div style="page-break-before: always;">
                        <h2>👀 정답지</h2>
                        <div class="box">
                            <strong>[2단계 정답]</strong><br>
                    """
                    for i, item in enumerate(quiz2, 1):
                        export_html += f"{i}) {item.get('word_display')} ({item.get('kor_def')})<br>"
                    
                    export_html += "</div><div class='box'><strong>[3단계 정답]</strong><br>"
                    for i, item in enumerate(quiz3, 1):
                        export_html += f"{i}) {item.get('word_in_example')}<br>"
                    
                    export_html += "</div></div></div></body></html>"

                    # 💡 [수정] 텍스트 다운로드 버튼 삭제 후 HTML 버튼만 크게 배치
                    st.download_button(
                        label="📥 모바일 전용 시험지 다운로드 (.html)",
                        data=export_html,
                        file_name=f"voca_quiz_{datetime.datetime.now().strftime('%m%d_%H%M')}.html",
                        mime="text/html",
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"오류가 발생했습니다. ({e})")

else:
    st.info("👈 위에서 사진을 찍거나 업로드하면 시험지가 생성됩니다!")
