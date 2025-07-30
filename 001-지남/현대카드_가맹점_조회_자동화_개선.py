
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

# 크롬 드라이버 설정
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# 현대카드 가맹점 검색 함수 (정확한 ID로 개선)
def search_hyundaicard_store(driver, keyword):
    try:
        driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "textMrchConmNm")))

        # 정확한 입력창 ID 사용
        search_input = driver.find_element(By.ID, "textMrchConmNm")
        search_input.clear()
        search_input.send_keys(keyword)

        # 검색 버튼 클릭
        driver.find_element(By.CLASS_NAME, "btn_srch").click()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "resultArea")))

        # 결과 판별
        page = driver.page_source
        return "검색 결과가 없습니다" not in page
    except Exception as e:
        print(f"[검색 실패] {keyword}: {e}")
        return False

# 데이터 불러오기 및 실행
df = pd.read_csv("지역화폐 가맹점 용인시 수지구.csv", encoding="cp949")
df["현대카드 가맹여부"] = ""

driver = setup_driver()
for i in range(len(df)):
    name = df.loc[i, '상호명']
    result = search_hyundaicard_store(driver, name)
    df.loc[i, "현대카드 가맹여부"] = "✅" if result else "❌"

driver.quit()
df.to_excel("현대카드_가맹점_조회결과.xlsx", index=False)
print("✅ 결과 저장 완료: 현대카드_가맹점_조회결과.xlsx")
