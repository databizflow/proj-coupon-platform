import streamlit as st
import time
from hyundaicard_checker import HyundaiCardChecker

def main():
    st.title("💳 현대카드 가맹점 단일 조회")

    store_name = st.text_input("🔍 검색할 상호명을 입력하세요", placeholder="예: 스타벅스")

    if st.button("가맹점 검색 시작"):
        with st.spinner("검색 중입니다..."):
            checker = HyundaiCardChecker()
            result_text = ""
            try:
                if checker.navigate_to_site():
                    result = checker.search_store(store_name)
                    if result == "O":
                        result_text = f"✅ '{store_name}'은 현대카드 가맹점입니다."
                    elif result == "X":
                        result_text = f"❌ '{store_name}'은 현대카드 가맹점이 아닙니다."
                    else:
                        result_text = f"⚠️ 오류 발생: {result}"
                else:
                    result_text = "❌ 사이트 접속 실패. 잠시 후 다시 시도해주세요."
            finally:
                checker.close()
            st.success(result_text)

if __name__ == "__main__":
    main()
