import streamlit as st
import google.generativeai as genai
import json
import random
from PIL import Image

# ----------------------------------------
# 1. 페이지 설정 및 초기화
# ----------------------------------------
st.set_page_config(page_title="영어 단어 시험지 생성기", page_icon="📝", layout="wide")
st.title("📸 사진으로 만드는 영어 단어 시험지 📝")

# Streamlit 서버의 비밀 금고에서 API 키 불러오기 (로컬 실행 시 st.secrets 대신 기존 config 사용)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("API 키를 찾을 수 없습니다. Streamlit Cloud의 Secrets 설정을 확인해주세요.")

# ----------------------------------------
# 2. 메인 로직 (이미지 업로드 및 촬영)
# ----------------------------------------
tab1, tab2 = st.tabs(["📁 앨범에서 업로드", "📸 카메라로 직접 촬영"])

with tab1:
    uploaded_file = st.file_uploader("단어장 사진을 업로드해주세요 (JPG, PNG)", type=["jpg", "jpeg", "png"])

with tab2:
    camera_photo = st.camera_input("카메라로 단어장을 찍어주세요")

final_image = uploaded_file or camera_photo

if final_image is not None:
    image = Image.open(final_image)
    st.image(image, caption="분석할 이미지", width=400)

    if st.button("🚀 시험지 생성하기"):
        with st.spinner("AI가 이미지를 분석하고 시험지를 만들고 있습니다... (약 10~20초 소요)"):
            try:
                model = genai.GenerativeModel('gemini-flash-latest')

                # 💡 [수정됨] 프롬프트: 과거형이 포함된 원문을 그대로 가져오도록 'word_display' 추가
                prompt = """
                당신은 영어 교육 전문가입니다. 첨부된 이미지에서 단어, 영어 뜻풀이, 예문을 추출하고 한국어로 번역하여 아래의 엄격한 JSON 형식으로만 반환하세요.
                마크다운 코드 블록(```json ... ```)을 사용하지 말고 오직 JSON 텍스트만 출력하세요.

                [조건]
                1. "word_display": 사진에 굵은 글씨로 적힌 단어 원문 전체 (과거형이 함께 적혀있다면 모두 포함, 예: 'press - pressed', 'through')
                2. "word": 빈칸 문제 정답 확인용 기본 단어 (예: 'press', 'through')
                3. "word_in_example": 예문 안에서 실제로 쓰인 형태 (예문이 'Robby was pressing...' 이면 'pressing') -> 빈칸 뚫기를 위해 매우 중요함!
                4. "eng_def": 사진에 적힌 영어 뜻풀이 (예: to push)
                5. "kor_def": "eng_def"의 한국어 해석 (단어의 뜻이 아니라 문장의 해석)
                6. "example": 사진에 적힌 영어 예문
                7. "example_kor": "example"의 한국어 해석

                [출력 예시]
                [
                  {
                    "word_display": "press - pressed",
                    "word": "press",
                    "word_in_example": "pressing",
                    "eng_def": "to push",
                    "kor_def": "누르다",
                    "example": "Robby was pressing buttons and moving controls.",
                    "example_kor": "Robby는 버튼을 누르며 조종 장치를 움직이고 있었다."
                  }
                ]
                """

                response = model.generate_content([prompt, image])
                
                result_text = response.text.strip()
                if result_text.startswith("```"):
                    result_text = result_text.split("\n", 1)[-1]
                    result_text = result_text.rsplit("\n", 1)[0]
                result_text = result_text.strip()

                st.success("데이터 추출 완료! 아래에서 결과를 확인하세요.")
                st.markdown("---")

                word_data = json.loads(result_text)

                if isinstance(word_data, dict):
                    for key in word_data:
                        if isinstance(word_data[key], list):
                            word_data = word_data[key]
                            break

                # ----------------------------------------
                # 3. 결과물 화면 출력
                # ----------------------------------------
                st.subheader("1. 영문뜻 + 한국어해석 + 예문 + 해석")
                for i, item in enumerate(word_data, 1):
                    # 💡 [수정됨] 단어 출력 시 과거형이 포함된 word_display 사용
                    word_display = item.get('word_display', item.get('word', 'N/A'))
                    eng_def = item.get('eng_def', 'N/A')
                    kor_def = item.get('kor_def', 'N/A')
                    example = item.get('example', 'N/A')
                    example_kor = item.get('example_kor', 'N/A')

                    st.markdown(f"**{i}. {word_display}**")
                    st.write(f"- 영문뜻: {eng_def}")
                    st.write(f"- 한국어해석: {kor_def}")
                    st.write(f"- 예문: {example}")
                    st.write(f"- 해석: {example_kor}")
                    st.write("")

                st.markdown("---")

                st.subheader("2. 영문뜻 → 단어/뜻 쓰기 (랜덤)")
                quiz2_data = word_data.copy()
                random.shuffle(quiz2_data)
                
                for item in quiz2_data:
                    st.write(f"- {item.get('eng_def', '')}")
                
                st.markdown("---")

                st.subheader("3. 예문 빈칸 문제 (랜덤)")
                quiz3_data = word_data.copy()
                random.shuffle(quiz3_data)

                for item in quiz3_data:
                    target_word = item.get('word_in_example', '')
                    example_text = item.get('example', '')
                    
                    if target_word and example_text:
                        blanked_example = example_text.replace(target_word, "______")
                        blanked_example = blanked_example.replace(target_word.capitalize(), "______")
                        st.write(f"- {blanked_example}")
                    else:
                        st.write(f"- {example_text}")

                st.markdown("---")

                st.subheader("4. 답지")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**[2번 답]**")
                    for item in quiz2_data:
                        # 💡 [수정됨] 답지에도 과거형이 포함된 세트로 출력
                        display_text = item.get('word_display', item.get('word', ''))
                        st.write(f"{display_text} - {item.get('kor_def', '')}")
                        
                with col2:
                    st.markdown("**[3번 답]**")
                    for item in quiz3_data:
                        st.write(item.get('word_in_example', ''))

                # ==========================================
                # 🚀 다운로드(저장) 기능 
                # ==========================================
                st.markdown("---")
                st.subheader("💾 만든 시험지 저장하기")
                
                export_text = "📝 나만의 영어 단어 시험지 📝\n\n"
                export_text += "[1. 단어 리스트]\n"
                for i, item in enumerate(word_data, 1):
                    export_text += f"{i}. {item.get('word_display', item.get('word', ''))}\n"
                    export_text += f"  - 영문뜻: {item.get('eng_def', '')}\n"
                    export_text += f"  - 한국어: {item.get('kor_def', '')}\n"
                    export_text += f"  - 예문: {item.get('example', '')}\n"
                    export_text += f"  - 해석: {item.get('example_kor', '')}\n\n"
                
                export_text += "------------------------\n\n[2. 영문뜻 보고 단어 맞추기]\n"
                for item in quiz2_data:
                    export_text += f"- {item.get('eng_def', '')}\n"
                
                export_text += "\n------------------------\n\n[3. 예문 빈칸 채우기]\n"
                for item in quiz3_data:
                    target = item.get('word_in_example', '')
                    ex = item.get('example', '')
                    if target and ex:
                        blanked = ex.replace(target, "______").replace(target.capitalize(), "______")
                        export_text += f"- {blanked}\n"
                    else:
                        export_text += f"- {ex}\n"
                
                export_text += "\n------------------------\n\n[정답지]\n"
                export_text += "2번 답:\n"
                for item in quiz2_data:
                    export_text += f"{item.get('word_display', item.get('word', ''))} - {item.get('kor_def', '')}\n"
                export_text += "\n3번 답:\n"
                for item in quiz3_data:
                    export_text += f"{item.get('word_in_example', '')}\n"

                st.download_button(
                    label="📥 텍스트 파일(.txt)로 다운로드",
                    data=export_text,
                    file_name="voca_quiz.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                st.write("프롬프트 결과가 JSON 형식이 아니거나, 이미지가 명확하지 않을 수 있습니다. 다시 시도해 보세요.")

elif final_image is None:
    st.info("단어장 사진을 업로드하거나 카메라로 촬영해 주세요.")
