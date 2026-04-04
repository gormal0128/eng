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
st.markdown("**영어 단어장 사진을 찍어 올리면, AI가 모든 영어의 품사와 발음까지 포함된 나만의 시험지를 만들어 줍니다! (누구나 무료)**")
st.markdown("---")

# Streamlit 서버의 비밀 금고에서 개발자의 API 키 불러오기
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("서버 점검 중입니다. 잠시 후 다시 시도해 주세요.")
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
        st.info("사진이 잘 올라왔어요! 이제 아래 버튼을 눌러주세요.")
        if st.button("🚀 AI 선생님! 시험지 만들어주세요!", use_container_width=True):
            with st.spinner("AI가 이미지를 분석하고 시험지를 만들고 있어요... (약 10~20초 소요)"):
                try:
                    model = genai.GenerativeModel('gemini-flash-latest')

                    # 💡 [명령 강화] 모든 영어 문장에 대해 한국어 발음을 추출하라는 명령을 추가
                    prompt = """
                    당신은 영어 교육 전문가입니다. 첨부된 이미지에서 단어, 영어 뜻풀이, 예문을 추출하고 한국어로 번역하여 아래의 엄격한 JSON 형식으로만 반환하세요.
                    마크다운 코드 블록(```json ... ```)을 사용하지 말고 오직 JSON 텍스트만 출력하세요.

                    [조건]
                    1. "part_of_speech": 사진에 적혀있는 품사 기호 (예: v., n., prep., adv., adj. 등. 만약 없다면 빈 문자열 "" 처리)
                    2. "word_display": 사진에 굵은 글씨로 적힌 단어 원문 전체 (과거형이 함께 적혀있다면 모두 포함, 예: 'press - pressed', 'through')
                    3. "pronunciation": "word_display"의 가장 정확하고 자연스러운 미국식 영어 발음을 한국어로 표기 (예: bright -> 브라이트. 한글만!!)
                    4. "word": 빈칸 문제 정답 확인용 기본 단어
                    5. "word_in_example": 예문 안에서 실제로 쓰인 형태
                    6. "eng_def": 사진에 적힌 영어 뜻풀이
                    7. "eng_def_pronunciation": "eng_def"의 가장 정확하고 자연스러운 미국식 영어 발음을 한국어로 표기 (예: from one side -> 프럼 원 사이드. 한글만!! 필수!!)
                    8. "kor_def": "eng_def"의 한국어 해석
                    9. "example": 사진에 적힌 영어 예문
                    10. "example_pronunciation": "example"의 가장 정확하고 자연스러운 미국식 영어 발음을 한국어로 표기 (예: Scott and Robby -> 스캇 앤 로비. 한글만!! 필수!!)
                    11. "example_kor": "example"의 한국어 해석
                    """

                    response = model.generate_content([prompt, image])
                    
                    result_text = response.text.strip()
                    if result_text.startswith("```"):
                        result_text = result_text.split("\n", 1)[-1]
                        result_text = result_text.rsplit("\n", 1)[0]
                    result_text = result_text.strip()

                    word_data = json.loads(result_text)

                    if isinstance(word_data, dict):
                        for key in word_data:
                            if isinstance(word_data[key], list):
                                word_data = word_data[key]
                                break

                    st.success("🎉 짜잔! 시험지가 완성되었어요! 아래로 내려서 확인해 보세요.")
                    
                    # ----------------------------------------
                    # 3. 결과물 화면 출력
                    # ----------------------------------------
                    st.markdown("---")
                    st.subheader("📖 1단계: 공부하기 (품사 + 단어 + 모든 영어 [발음])")
                    for i, item in enumerate(word_data, 1):
                        pos = item.get('part_of_speech', '')
                        if pos: pos = f"{pos} " 
                        
                        pronun = item.get('pronunciation', '')
                        if pronun: pronun = f"[{pronun}]" # 한국어 발음에 괄호 씌우기
                        
                        word_display = item.get('word_display', item.get('word', 'N/A'))
                        eng_def = item.get('eng_def', 'N/A')
                        
                        # 💡 [발음 추가] 뜻풀이의 영어 발음을 가져와 괄호로 묶음
                        eng_def_pronun = item.get('eng_def_pronunciation', '')
                        if eng_def_pronun: eng_def_pronun = f"[{eng_def_pronun}]"

                        kor_def = item.get('kor_def', 'N/A')
                        example = item.get('example', 'N/A')
                        
                        # 💡 [발음 추가] 예문의 영어 발음을 가져와 괄호로 묶음
                        example_pronun = item.get('example_pronunciation', '')
                        if example_pronun: example_pronun = f"[{example_pronun}]"

                        example_kor = item.get('example_kor', 'N/A')

                        st.markdown(f"**{i}) {pos}{word_display} {pronun}**")
                        # 💡 [화면 출력 수호] 뜻풀이와 예문에 발음([발음]) 추가
                        st.write(f"  🇺🇸 영문뜻: {eng_def} {eng_def_pronun}  \n  🇰🇷 뜻해석: {kor_def}")
                        st.write(f"  📝 예문: {example} {example_pronun}  \n  🗣️ 예문해석: {example_kor}")
                        st.write("")

                    st.markdown("---")
                    st.subheader("🎯 2단계: 시험 1 (뜻 보고 단어 맞추기)")
                    quiz2_data = word_data.copy()
                    random.shuffle(quiz2_data)
                    for i, item in enumerate(quiz2_data, 1):
                        # 💡 [시험 수호] 시험 문제에도 뜻풀이의 영어와 함께 발음을 출력
                        eng_def_pronun = item.get('eng_def_pronunciation', '')
                        if eng_def_pronun: eng_def_pronun = f"[{eng_def_pronun}]"
                        st.write(f"**{i})** {item.get('eng_def', '')} {eng_def_pronun}")
                    
                    st.markdown("---")
                    st.subheader("🎯 3단계: 시험 2 (예문 빈칸 채우기)")
                    quiz3_data = word_data.copy()
                    random.shuffle(quiz3_data)
                    for i, item in enumerate(quiz3_data, 1):
                        target_word = item.get('word_in_example', '')
                        example_text = item.get('example', '')
                        # New field
                        example_pronun = item.get('example_pronunciation', '')
                        if example_pronun: example_pronun = f"[{example_pronun}]"

                        if target_word and example_text:
                            blanked_example = example_text.replace(target_word, "______").replace(target_word.capitalize(), "______")
                            # 💡 [시험 수호] 시험 문제에도 예문의 영어와 함께 발음을 출력
                            st.write(f"**{i})** {blanked_example} {example_pronun}")
                        else:
                            st.write(f"**{i})** {example_text} {example_pronun}")

                    st.markdown("---")
                    with st.expander("👀 정답지 확인하기 (클릭!)"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**[시험 1 정답]**")
                            for i, item in enumerate(quiz2_data, 1):
                                pos = item.get('part_of_speech', '')
                                if pos: pos = f"{pos} "
                                pronun = item.get('pronunciation', '')
                                if pronun: pronun = f"[{pronun}]"
                                display_text = item.get('word_display', item.get('word', ''))
                                st.write(f"**{i})** {pos}{display_text} {pronun} - {item.get('kor_def', '')}")
                                
                        with c2:
                            st.markdown("**[시험 2 정답]**")
                            for i, item in enumerate(quiz3_data, 1):
                                # 💡 [답지 수호] 답지에도 단어의 원문과 함께 발음을 포함시켜 더 명확하게 함
                                pronun = item.get('pronunciation', '')
                                if pronun: pronun = f"[{pronun}]"
                                display_text = item.get('word_display', item.get('word', ''))
                                st.write(f"**{i})** {display_text} {pronun}")

                    # ----------------------------------------
                    # 4. 저장 기능
                    # ----------------------------------------
                    st.markdown("---")
                    st.subheader("💾 나만의 시험지 저장하기")
                    st.write("다 만든 시험지를 핸드폰이나 컴퓨터에 텍스트 파일로 저장해서 프린트해 보세요!")
                    
                    export_text = "📝 나만의 영어 단어 시험지 📝\n\n"
                    export_text += "[1. 단어 리스트]\n"
                    for i, item in enumerate(word_data, 1):
                        pos = item.get('part_of_speech', '')
                        if pos: pos = f"{pos} "
                        pronun = item.get('pronunciation', '')
                        if pronun: pronun = f"[{pronun}]"
                        
                        # New fields
                        eng_def_pronun = item.get('eng_def_pronunciation', '')
                        if eng_def_pronun: eng_def_pronun = f"[{eng_def_pronun}]"
                        example_pronun = item.get('example_pronunciation', '')
                        if example_pronun: example_pronun = f"[{example_pronun}]"

                        export_text += f"{i}) {pos}{item.get('word_display', item.get('word', ''))} {pronun}\n"
                        # 💡 [저장 수호] 저장되는 텍스트 파일에도 뜻풀이와 예문에 발음([발음]) 추가
                        export_text += f"  - 뜻: {item.get('eng_def', '')} {eng_def_pronun} ({item.get('kor_def', '')})\n"
                        export_text += f"  - 예문: {item.get('example', '')} {example_pronun}\n"
                        export_text += f"  - 해석: {item.get('example_kor', '')}\n\n"
                    
                    export_text += "------------------------\n\n[2. 뜻 보고 단어 맞추기]\n"
                    for i, item in enumerate(quiz2_data, 1):
                        # 💡 [저장 수호] 저장되는 텍스트 파일의 시험 문제에도 뜻풀이의 영어와 함께 발음을 출력
                        eng_def_pronun = item.get('eng_def_pronunciation', '')
                        if eng_def_pronun: eng_def_pronun = f"[{eng_def_pronun}]"
                        export_text += f"{i}) {item.get('eng_def', '')} {eng_def_pronun}\n"
                    
                    export_text += "\n------------------------\n\n[3. 예문 빈칸 채우기]\n"
                    for i, item in enumerate(quiz3_data, 1):
                        target = item.get('word_in_example', '')
                        ex = item.get('example', '')
                        # New field
                        example_pronun = item.get('example_pronunciation', '')
                        if example_pronun: example_pronun = f"[{example_pronun}]"

                        if target and ex:
                            export_text += f"{i}) {ex.replace(target, '______').replace(target.capitalize(), '______')} {example_pronun}\n"
                        else:
                            export_text += f"{i}) {ex} {example_pronun}\n"
                    
                    export_text += "\n------------------------\n\n[정답지]\n"
                    export_text += "시험 1 답:\n"
                    for i, item in enumerate(quiz2_data, 1):
                        pos = item.get('part_of_speech', '')
                        if pos: pos = f"{pos} "
                        pronun = item.get('pronunciation', '')
                        if pronun: pronun = f"[{pronun}]"
                        export_text += f"{i}) {pos}{item.get('word_display', item.get('word', ''))} {pronun} - {item.get('kor_def', '')}\n"
                        
                    export_text += "\n시험 2 답:\n"
                    for i, item in enumerate(quiz3_data, 1):
                        # 💡 [답지 수호] 저장되는 텍스트 파일 답지에도 단어의 원문과 함께 발음을 포함
                        pronun = item.get('pronunciation', '')
                        if pronun: pronun = f"[{pronun}]"
                        display_text = item.get('word_display', item.get('word', ''))
                        export_text += f"{i}) {display_text} {pronun}\n"

                    st.download_button(
                        label="📥 텍스트 파일(.txt)로 다운로드",
                        data=export_text,
                        file_name="voca_quiz.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        st.error("앗! 오늘 사용자들이 너무 많아서 일일 무료 이용량이 다 떨어졌어요! 😭 내일 다시 접속해 주세요.")
                    else:
                        st.error("오류가 발생했어요. 사진이 너무 흐리거나 텍스트를 찾을 수 없나 봐요. 다른 사진으로 시도해 볼까요?")

else:
    st.info("👈 위에서 카메라로 바로 찍거나, 사진첩에서 골라주세요!")
