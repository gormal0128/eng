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
st.markdown("**영어 단어장 사진을 찍어 올리면, 모든 영어 문장에 한글 발음을 붙여서 시험지를 만들어 드립니다!**")
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
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(image, caption="내가 올린 사진", use_container_width=True)
        
    with col2:
        st.info("사진 분석 준비 완료! 버튼을 눌러주세요.")
        if st.button("🚀 모든 영어에 발음 넣어서 시험지 만들기!", use_container_width=True):
            with st.spinner("AI가 모든 문장의 발음을 한글로 적고 있어요... (약 15~20초 소요)"):
                try:
                    model = genai.GenerativeModel('gemini-flash-latest')

                    # 💡 [프롬프트 대폭 강화] 모든 영어 필드에 대해 한글 발음을 필수적으로 요구
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
                    
                    # 결과 텍스트 정제
                    result_text = response.text.strip()
                    if result_text.startswith("```"):
                        result_text = result_text.split("\n", 1)[-1].rsplit("\n", 1)[0]
                    word_data = json.loads(result_text)

                    if isinstance(word_data, dict):
                        for key in word_data:
                            if isinstance(word_data[key], list):
                                word_data = word_data[key]
                                break

                    st.success("🎉 발음까지 완벽한 시험지가 완성되었습니다!")
                    
                    # ----------------------------------------
                    # 3. 화면 출력 (공부하기 단계)
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

                    # ----------------------------------------
                    # 4. 시험 문제 단계 (랜덤 셔플)
                    # ----------------------------------------
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
                    # 5. 정답지 및 다운로드
                    # ----------------------------------------
                    st.markdown("---")
                    with st.expander("👀 정답 확인하기"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**[시험 2 정답]**")
                            for i, item in enumerate(quiz2, 1):
                                st.write(f"{i}) {item.get('word_display')} ({item.get('kor_def')})")
                        with c2:
                            st.markdown("**[시험 3 정답]**")
                            for i, item in enumerate(quiz3, 1):
                                st.write(f"{i}) {item.get('word_in_example')}")

                    # 텍스트 저장용 데이터 생성
                    export_text = "📝 모든 영어 발음이 포함된 단어 시험지 📝\n\n"
                    for i, item in enumerate(word_data, 1):
                        export_text += f"{i}) {item.get('word_display')} [{item.get('word_pronun')}]\n"
                        export_text += f"   뜻: {item.get('eng_def')} [{item.get('eng_def_pronun')}]\n"
                        export_text += f"   해석: {item.get('kor_def')}\n"
                        export_text += f"   예문: {item.get('example')} [{item.get('example_pronun')}]\n"
                        export_text += f"   해석: {item.get('example_kor')}\n\n"

                    st.download_button("📥 텍스트 파일로 저장", export_text, file_name="voca_study.txt", use_container_width=True)

                except Exception as e:
                    st.error(f"오류가 발생했습니다. 사진을 다시 찍어보세요! ({e})")

else:
    st.info("👈 위에서 사진을 찍거나 업로드하면 시험지가 생성됩니다!")
