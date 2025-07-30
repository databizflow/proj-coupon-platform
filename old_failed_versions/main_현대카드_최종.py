from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def search_hyundaicard_merchants(input_csv, output_csv):
    df = pd.read_csv(input_csv, encoding='cp949')
    df['현대카드_가맹여부'] = ''

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    for idx, row in df.iterrows():
        try:
            print(f"처리 중: {idx+1}/{len(df)} - {row.get('상호명', row.iloc[0])}")
            
            # 페이지 접속
            driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
            time.sleep(3)
            
            # 상호명 입력 (지역은 이미 선택되어 있음)
            store_name = row.get('상호명', row.iloc[0])
            store_input = wait.until(EC.presence_of_element_located((By.ID, "textMrchConmNm")))
            store_input.clear()
            store_input.send_keys(store_name)
            
            # 검색 버튼 클릭
            search_button = driver.find_element(By.ID, "storeSearch")
            search_button.click()
            time.sleep(4)
            
            # 결과 확인 (상세 디버깅)
            print("=== 결과 분석 시작 ===")
            
            # 1. 페이지 텍스트에서 결과 없음 메시지 확인
            page_source = driver.page_source
            if "0건이 검색되었습니다" in page_source:
                result = 'X'
                print("결과: 없음 (0건 메시지)")
            elif "검색 결과가 없습니다" in page_source:
                result = 'X'
                print("결과: 없음 (결과 없음 메시지)")
            else:
                # 2. storeSearchList 요소 확인
                try:
                    store_search_list = driver.find_element(By.ID, "storeSearchList")
                    display_style = store_search_list.get_attribute("style")
                    print(f"storeSearchList style: {display_style}")
                    
                    if "display: block" in display_style:
                        print("storeSearchList가 표시됨")
                        
                        # 3. resultList 확인
                        try:
                            result_list = driver.find_element(By.ID, "resultList")
                            rows = result_list.find_elements(By.TAG_NAME, "tr")
                            print(f"resultList 행 개수: {len(rows)}")
                            
                            if len(rows) > 0:
                                first_row = rows[0]
                                cells = first_row.find_elements(By.TAG_NAME, "td")
                                print(f"첫 번째 행 셀 개수: {len(cells)}")
                                
                                if len(cells) >= 2:
                                    store_name_cell = cells[1].text.strip()
                                    print(f"가맹점명: '{store_name_cell}'")
                                    
                                    if store_name_cell:
                                        result = 'O'
                                        print(f"결과: 있음 - {store_name_cell}")
                                    else:
                                        result = 'X'
                                        print("결과: 없음 (빈 가맹점명)")
                                else:
                                    result = 'X'
                                    print("결과: 없음 (셀 부족)")
                            else:
                                result = 'X'
                                print("결과: 없음 (행 없음)")
                        except Exception as e:
                            result = 'X'
                            print(f"resultList 오류: {e}")
                    else:
                        result = 'X'
                        print("storeSearchList가 숨겨짐")
                        
                except Exception as e:
                    result = 'X'
                    print(f"storeSearchList 오류: {e}")
            
            print("=== 결과 분석 완료 ===")
            
            df.at[idx, '현대카드_가맹여부'] = result
            print(f"최종: {result}")
            
        except Exception as e:
            print(f"오류: {e}")
            df.at[idx, '현대카드_가맹여부'] = '오류'
            continue

    # 결과 저장
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    driver.quit()
    print(f"완료! 결과: {output_csv}")

if __name__ == "__main__":
    input_path = "suji.csv"
    output_path = "현대카드_가맹점_조회결과_최종.csv"
    search_hyundaicard_merchants(input_path, output_path)