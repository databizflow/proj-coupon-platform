
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def search_hyundaicard_merchants(input_csv, output_csv):
    df = pd.read_csv(input_csv, encoding='cp949')
    df['현대카드_가맹여부'] = ''

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    for idx, row in df.iterrows():
        try:
            driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
            wait.until(EC.presence_of_element_located((By.ID, "searchSido")))

            # 시도 선택
            Select(driver.find_element(By.ID, "searchSido")).select_by_visible_text("경기")
            time.sleep(0.5)

            # 시군구 선택
            Select(driver.find_element(By.ID, "ajaxView_Sigungu")).select_by_visible_text("용인시 수지구")
            time.sleep(0.5)

            # 동(읍면동) 선택 - 비워둘 수도 있음
            dong_list = driver.find_element(By.ID, "ajaxView_Dong").text
            dong_to_select = "풍덕천1동" if "풍덕천1동" in dong_list else driver.find_element(By.ID, "ajaxView_Dong").find_elements(By.TAG_NAME, "option")[1].text
            Select(driver.find_element(By.ID, "ajaxView_Dong")).select_by_visible_text(dong_to_select)
            time.sleep(0.5)

            # 상호명 입력
            store_name = row['상호명'] if '상호명' in row else row[0]
            driver.find_element(By.ID, "textMrchConmNm").send_keys(store_name)

            # 검색 버튼 클릭
            driver.find_element(By.ID, "storeSearch").click()
            time.sleep(2)

            # 결과 유무 확인
            page_source = driver.page_source
            if "검색 결과가 없습니다" in page_source:
                df.at[idx, '현대카드_가맹여부'] = 'X'
            else:
                df.at[idx, '현대카드_가맹여부'] = 'O'
        except Exception as e:
            df.at[idx, '현대카드_가맹여부'] = f"오류: {e}"
            continue

    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    driver.quit()

# 실행 예시
if __name__ == "__main__":
    input_path = "지역화폐_가맹점_용인시_수지구.csv"
    output_path = "현대카드_가맹점_조회결과.csv"
    search_hyundaicard_merchants(input_path, output_path)
