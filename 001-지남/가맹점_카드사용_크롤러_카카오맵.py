
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# 엑셀 파일명
input_file = "yongin.csv"
output_file = "가맹점_카드사용_결과_카카오맵.xlsx"

# 크롬 옵션 설정
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

# 데이터 불러오기
df = pd.read_csv(input_file, encoding="cp949")
df[['신한카드', '국민카드', 'BC카드']] = ""

# 드라이버 실행
driver = webdriver.Chrome(options=options)

def search_kakao_map_info(store_name, store_addr):
    try:
        query = f"{store_name} {store_addr}"
        driver.get("https://map.kakao.com/")
        time.sleep(2)

        search_box = driver.find_element(By.ID, "search.keyword.query")
        search_box.clear()
        search_box.send_keys(query)

        search_button = driver.find_element(By.ID, "search.keyword.submit")
        search_button.click()
        time.sleep(3)

        # 결과 프레임으로 전환
        driver.switch_to.frame("searchIframe")
        time.sleep(2)

        page_text = driver.page_source
        result = {
            '신한카드': '카드결제' in page_text,
            '국민카드': '카드결제' in page_text,
            'BC카드': '카드결제' in page_text
        }

        return {k: "✅" if v else "❌" for k, v in result.items()}
    except Exception as e:
        print(f"[검색 실패] {query}: {e}")
        return {'신한카드': '오류', '국민카드': '오류', 'BC카드': '오류'}

# 상위 5개만 테스트
for i in range(min(5, len(df))):
    name = df.loc[i, '상호명']
    addr = df.loc[i, '소재지도로명주소']
    result = search_kakao_map_info(name, addr)
    df.loc[i, ['신한카드', '국민카드', 'BC카드']] = list(result.values())

driver.quit()
df.to_excel(output_file, index=False)
print("결과 저장 완료:", output_file)
