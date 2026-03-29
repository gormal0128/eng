import streamlit as st
import google.generativeai as genai
import json
import random
from PIL import Image

# Streamlit 서버의 비밀 금고에서 API 키 불러오기
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ----------------------------------------
# 1. 페이지 설정 및 초기화
# ----------------------------------------
st.set_page_config(page_title="영어 단어 시험지 생성기", page_icon="📝", layout="wide")
st.title("📸 사진으로 만드는 영어 단어 시험지 📝")


# ----------------------------------------
# 2. 메인 로직 (이미지 업로드 및 촬영)
# ----------------------------------------

# 탭을 생성하여 두 가지 입력 방식을 제공합니다.
tab1, tab2 = st.tabs(["📁 앨범에서 업로드", "📸 카메라로 직접 촬영"])

with tab1:
    uploaded_file = st.file_uploader("단어장 사진을 업로드해주세요 (JPG, PNG)", type=["jpg", "jpeg", "png"])

with tab2:
    camera_photo = st.camera_input("카메라로 단어장을 찍어주세요")

# 업로드된 파일이나 촬영된 사진 중 하나라도 있으면 진행합니다.
# 둘 다 있을 경우(그럴 일은 적지만) 업로드된 파일을 우선시합니다.
final_image = uploaded_file or camera_photo

if final_image is not None:
    # 이미지 화면에 보여주기
    image = Image.open(final_image)
    st.image(image, caption="분석할 이미지", width=400)

    # 처리 버튼
    if st.button("🚀 시험지 생성하기"):
        with st.spinner("AI가 이미지를 분석하고 시험지를 만들고 있습니다... (약 10~20초 소요)"):
            try:
                # 사용자가 지정한 최신 Flash 모델 사용
                model = genai.GenerativeModel('gemini-flash-latest')

                # (이하 기존 프롬프트 및 API 호출 로직은 이전 코드와 완전히 동일합니다)
                prompt = """
                당신은 영어 교육 전문가입니다. 첨부된 이미지에서 단어, 영어 뜻풀이, 예문을 추출하고 한국어로 번역하여 아래의 엄격한 JSON 형식으로만 반환하세요.
                마크다운 코드 블록(```json ... ```)을 사용하지 말고 오직 JSON 텍스트만 출력하세요.

                [조건]
                1. "word": 기본 단어 (예: press)
                2. "word_in_example": 예문 안에서 실제로 쓰인 형태 (예문이 'Robby was pressing...' 이면 'pressing') -> 빈칸 뚫기를 위해 매우 중요함!
                3. "eng_def": 사진에 적힌 영어 뜻풀이 (예: to push)
                4. "kor_def": "eng_def"의 한국어 해석 (단어의 뜻이 아니라 문장의 해석)
                5. "example": 사진에 적힌 영어 예문
                6. "example_kor": "example"의 한국어 해석

                [출력 예시]
                [
                  {
                    "word": "press",
                    "word_in_example": "pressing",
                    "eng_def": "to push",
                    "kor_def": "누르다",
                    "example": "Robby was pressing buttons and moving controls.",
                    "example_kor": "Robby는 버튼을 누르며 조종 장치를 움직이고 있었다."
                  }
                ]
                """

                # API 호출
                response = model.generate_content([prompt, image])
                
                # 응답에서 불필요한 마크다운 텍스트 제거 (안전장치)
                result_text = response.text.strip().removeprefix('```json').removesuffix('```').strip()
                
                # JSON 파싱
                word_data = json.loads(result_text)

                st.success("데이터 추출 완료! 아래에서 결과를 확인하세요.")
                st.markdown("---")

                # (이하 결과물 출력 부분도 이전 코드와 동일하게 유지하세요)
                
                # ... [요구사항 1, 2, 3, 4 출력 로직] ...
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                st.write("프롬프트 결과가 JSON 형식이 아니거나, 이미지가 명확하지 않을 수 있습니다. 다시 시도해 보세요.")

# JSON 파싱
                word_data = json.loads(result_text)

                st.success("데이터 추출 완료! 아래에서 결과를 확인하세요.")
                st.markdown("---")

                # ----------------------------------------
                # 3. 결과물 화면 출력
                # ----------------------------------------

                # [요구사항 1] 전체 리스트 출력
                st.subheader("1. 영문뜻 + 한국어해석 + 예문 + 해석")
                for i, item in enumerate(word_data, 1):
                    st.markdown(f"**{i}. {item['word']}**")
                    st.write(f"- 영문뜻: {item['eng_def']}")
                    st.write(f"- 한국어해석: {item['kor_def']}")
                    st.write(f"- 예문: {item['example']}")
                    st.write(f"- 해석: {item['example_kor']}")
                    st.write("")

                st.markdown("---")

                # [요구사항 2] 뜻 보고 단어 맞추기 (랜덤)
                st.subheader("2. 영문뜻 → 단어/뜻 쓰기 (랜덤)")
                quiz2_data = word_data.copy()
                random.shuffle(quiz2_data)
                
                for item in quiz2_data:
                    st.write(f"- {item['eng_def']}")
                
                st.markdown("---")

                # [요구사항 3] 예문 빈칸 문제 (랜덤)
                st.subheader("3. 예문 빈칸 문제 (랜덤)")
                quiz3_data = word_data.copy()
                random.shuffle(quiz3_data)

                for item in quiz3_data:
                    target_word = item['word_in_example']
                    blanked_example = item['example'].replace(target_word, "______")
                    blanked_example = blanked_example.replace(target_word.capitalize(), "______")
                    
                    st.write(f"- {blanked_example}")

                st.markdown("---")

                # [요구사항 4] 답지
                st.subheader("4. 답지")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**[2번 답]**")
                    for item in quiz2_data:
                        st.write(f"{item['word']} - {item['kor_def']}")
                        
                with col2:
                    st.markdown("**[3번 답]**")
                    for item in quiz3_data:
                        st.write(item['word_in_example'])

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                st.write("프롬프트 결과가 JSON 형식이 아니거나, 이미지가 명확하지 않을 수 있습니다. 다시 시도해 보세요.")

elif uploaded_file is None:
    st.info("단어장 사진을 업로드 해주세요.")
