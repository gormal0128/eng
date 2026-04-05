import streamlit as st
import google.generativeai as genai
import json
import random
from PIL import Image

# ----------------------------------------
# 1. 페이지 설정 및 초기화
# ----------------------------------------
st.set_page_config(page_title="찰칵! AI 영어 단어장", page_icon="📸", layout="wide")

st.title("📸 찰칵! AI 영어 시험지 메이커 📝")
st.markdown("**모바일에서도 잘 보이는 HTML 문서 저장 기능이 추가되었습니다!**")
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
        if st.button("🚀 모든 영어에 발음 넣어서 시험지 만들기!", use_container_width=True):
            with st.spinner("AI가 모든 문장에 한글 발음을 입히고 있어요... (약 15~20초 소요)"):
                try:
                    model = genai.GenerativeModel('gemini-flash-latest')

                    prompt = """
                    당신은 영어 교육 전문가입니다. 첨부된 이미지에서 단어, 뜻풀이, 예문을 추출하고 아래 JSON 형식으로 반환하세요.
                    
                    [필수 규칙: 모든 영어에는 반드시 한국어 발음을 추가하세요]
                    1. "word_display": 사진 속 단어 원문 (예: press - pressed)
                    2. "word_pronun": "word_display"의 한글 발음 (예: 프레스 - 프레스트)
                    3. "eng_def": 영어 뜻풀이 원문
                    4. "eng_def_pronun": "eng_def" 전체 문장의 한글 발음 (예: [프롬 원 사이드 투 언아더 사이드 오브 썸띵])
                    5. "example": 영어 예문 원문
                    6. "example_pronun": "example" 전체 문장의 한글 발음 (예: [스콧 앤 로비 점프드 뚜루 더 도어])
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
                    st.subheader("📖 1단계: 발음과 함께 공부하기")
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
                        st.write(f"  🇺🇸 **뜻:** {eng_def}  \n  🗣️ **발음:** {eng_def_pron}  \n  🇰🇷 **해석:** {kor_def}")
                        st.write(f"  📝 **예문:** {example}  \n  🗣️ **발음:** {example_pron}  \n  🇰🇷 **해석:** {example_kor}")
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
                        ex_pron = item.get('example_pronun', '')
                        if target:
                            blanked = ex_text.replace(target, "______").replace(target.capitalize(), "______")
                            st.write(f"**{i})** {blanked} [{ex_pron}]")
                        else:
                            st.write(f"**{i})** {ex_text} [{ex_pron}]")

                    # ----------------------------------------
                    # 4. 저장 데이터 생성 (TXT 및 HTML)
                    # ----------------------------------------
                    st.markdown("---")
                    st.subheader("💾 시험지 저장하기 (모바일 추천: HTML)")
                    
                    # --- TXT 데이터 생성 ---
                    export_txt = "📝 영어 단어 시험지 (TXT 버전)\n\n"
                    for i, item in enumerate(word_data, 1):
                        export_txt += f"{i}) {item.get('word_display')} [{item.get('word_pronun')}]\n"
                        export_txt += f"   뜻: {item.get('eng_def')} [{item.get('eng_def_pronun')}]\n"
                        export_txt += f"   해석: {item.get('kor_def')}\n"
                        export_txt += f"   예문: {item.get('example')} [{item.get('example_pronun')}]\n"
                        export_txt += f"   해석: {item.get('example_kor')}\n\n"

                    # --- HTML 데이터 생성 (모바일 가독성 최적화) ---
                    export_html = f"""
                    <!DOCTYPE html>
                    <html lang="ko">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            body {{ font-family: sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f9; padding: 15px; }}
                            .container {{ max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                            h1 {{ text-align: center; color: #2c3e50; font-size: 1.4em; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                            h2 {{ color: #e67e22; border-left: 5px solid #e67e22; padding-left: 10px; margin-top: 30px; font-size: 1.1em; }}
                            .item {{ margin-bottom: 20px; padding: 10px; border-bottom: 1px solid #eee; }}
                            .word {{ font-size: 1.1em; font-weight: bold; color: #2980b9; }}
                            .pronun {{ color: #e74c3c; font-weight: normal; font-size: 0.9em; }}
                            .eng {{ color: #2c3e50; font-weight: bold; display: block; margin-top: 5px; }}
                            .kor {{ color: #7f8c8d; font-size: 0.9em; display: block; }}
                            .box {{ background: #f9f9f9; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 0.95em; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>📝 AI 영어 단어 시험지</h1>
                            <h2>1단계: 공부하기</h2>
                    """
                    for i, item in enumerate(word_data, 1):
                        export_html += f"""
                        <div class="item">
                            <span class="word">{i}) {item.get('part_of_speech', '')} {item.get('word_display')}</span> 
                            <span class="pronun">[{item.get('word_pronun')}]</span>
                            <div class="box">
                                <span class="eng">뜻: {item.get('eng_def')}</span>
                                <span class="pronun">[{item.get('eng_def_pronun')}]</span>
                                <span class="kor">해석: {item.get('kor_def')}</span>
                            </div>
                            <div class="box" style="background:#fffbe6;">
                                <span class="eng">예문: {item.get('example')}</span>
                                <span class="pronun">[{item.get('example_pronun')}]</span>
                                <span class="kor">해석: {item.get('example_kor')}</span>
                            </div>
                        </div>
                        """
                    
                    # 퀴즈 및 정답 섹션 추가
                    export_html += "<h2>2단계: 뜻 보고 단어 쓰기</h2>"
                    for i, item in enumerate(quiz2, 1):
                        export_html += f"<div class='item'>{i}) {item.get('eng_def')} <br><small class='pronun'>[{item.get('eng_def_pronun')}]</small></div>"
                    
                    export_html += "<h2>3단계: 예문 빈칸 채우기</h2>"
                    for i, item in enumerate(quiz3, 1):
                        target = item.get('word_in_example', '')
                        ex_text = item.get('example', '')
                        ex_pron = item.get('example_pronun', '')
                        blanked = ex_text.replace(target, "______").replace(target.capitalize(), "______") if target else ex_text
                        export_html += f"<div class='item'>{i}) {blanked} <br><small class='pronun'>[{ex_pron}]</small></div>"

                    export_html += "</div></body></html>"

                    # 다운로드 버튼 레이아웃
                    col_txt, col_html = st.columns(2)
                    with col_txt:
                        st.download_button("📄 텍스트 파일(.txt) 다운로드", export_txt, file_name="voca_quiz.txt", use_container_width=True)
                    with col_html:
                        st.download_button("🌐 HTML 문서(.html) 다운로드", export_html, file_name="voca_quiz.html", mime="text/html", use_container_width=True)

                except Exception as e:
                    st.error(f"오류가 발생했습니다. ({e})")

else:
    st.info("👈 사진을 찍거나 업로드하면 시험지가 생성됩니다!")
