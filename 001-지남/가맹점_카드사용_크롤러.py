
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# 엑셀 파일명 (사용자 파일명에 맞게 수정)
input_file = "yongin.csv"
output_file = "가맹점_카드사용_결과.xlsx"

# 크롬 옵션
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

# 데이터 로드
df = pd.read_csv(input_file, encoding="cp949")
df[['신한카드', '국민카드', 'BC카드']] = ""

# 크롬 드라이버 실행
driver = webdriver.Chrome(options=options)

def search_card_info(store_name, store_addr):
    try:
        query = f"{store_name} {store_addr}"
        driver.get(f"https://map.naver.com/p/search/{query}")
        time.sleep(3)
        
        if "entryIframe" in [frame.get_attribute("name") for frame in driver.find_elements(By.TAG_NAME, "iframe")]:
            driver.switch_to.frame("entryIframe")
            time.sleep(2)
            page_text = driver.page_source
            ...
        else:
            print(f"iframe 미탐지: {query}")

        driver.switch_to.frame("entryIframe")
        time.sleep(2)

        page_text = driver.page_source
        result = {
            '신한카드': '신한카드' in page_text,
            '국민카드': '국민카드' in page_text,
            'BC카드': 'BC카드' in page_text
        }
        return {k: "✅" if v else "❌" for k, v in result.items()}
    except Exception as e:
        return {'신한카드': '오류', '국민카드': '오류', 'BC카드': '오류'}

# 상위 5개만 테스트
for i in range(min(5, len(df))):
    name = df.loc[i, '상호명']
    addr = df.loc[i, '소재지도로명주소']
    result = search_card_info(name, addr)
    df.loc[i, ['신한카드', '국민카드', 'BC카드']] = list(result.values())

driver.quit()

# 결과 저장
df.to_excel(output_file, index=False)
print("결과 저장 완료:", output_file)
