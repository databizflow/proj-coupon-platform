from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def search_hyundaicard_merchants(input_csv, output_csv):
    df = pd.read_csv(input_csv, encoding='cp949')
    df['현대카드_가맹여부'] = ''

    # Chrome 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    for idx, row in df.iterrows():
        try:
            print(f"처리 중: {idx+1}/{len(df)} - {row.get('상호명', row.iloc[0])}")
            
            # 현대카드 가맹점 조회 페이지 접속
            driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
            time.sleep(5)
            
            # 1. 경기도 선택 (Selenium Select 사용)
            try:
                sido_select = Select(driver.find_element(By.ID, "searchSido"))
                sido_select.select_by_value("경기")
                print("경기도 선택 성공")
                time.sleep(3)
            except Exception as e:
                print(f"경기도 선택 실패: {e}")
                df.at[idx, '현대카드_가맹여부'] = '오류: 경기도 선택 실패'
                continue
            
            # 2. 용인시 수지구 선택
            try:
                sigungu_select = Select(driver.find_element(By.ID, "ajaxView_Sigungu"))
                # 옵션이 로드될 때까지 대기
                for attempt in range(10):
                    try:
                        sigungu_select.select_by_value("용인시 수지구")
                        print("용인시 수지구 선택 성공")
                        break
                    except:
                        print(f"용인시 수지구 선택 시도 {attempt + 1}")
                        time.sleep(2)
                        sigungu_select = Select(driver.find_element(By.ID, "ajaxView_Sigungu"))
                else:
                    print("용인시 수지구 선택 실패")
                    df.at[idx, '현대카드_가맹여부'] = '오류: 시군구 선택 실패'
                    continue
                    
                time.sleep(2)
            except Exception as e:
                print(f"시군구 선택 중 오류: {e}")
                df.at[idx, '현대카드_가맹여부'] = '오류: 시군구 선택 오류'
                continue
            
            # 3. 상호명 입력 및 검색
            store_name = row.get('상호명', row.iloc[0])
            try:
                store_input = driver.find_element(By.ID, "textMrchConmNm")
                store_input.clear()
                store_input.send_keys(store_name)
                
                search_button = driver.find_element(By.ID, "storeSearch")
                search_button.click()
                print(f"'{store_name}' 검색 실행")
                time.sleep(5)
            except Exception as e:
                print(f"검색 실행 실패: {e}")
                df.at[idx, '현대카드_가맹여부'] = '오류: 검색 실행 실패'
                continue
            
            # 4. 결과 확인 (간단하게)
            try:
                page_text = driver.page_source
                
                # 결과 없음 패턴 확인
                if ("0건이 검색되었습니다" in page_text or 
                    "검색 결과가 없습니다" in page_text or
                    "검색결과가 없습니다" in page_text):
                    result = 'X'
                    print("검색 결과: 없음")
                else:
                    # resultList 확인
                    try:
                        result_list = driver.find_element(By.ID, "resultList")
                        rows = result_list.find_elements(By.TAG_NAME, "tr")
                        if len(rows) > 0:
                            result = 'O'
                            print(f"검색 결과: 있음 ({len(rows)}개)")
                        else:
                            result = 'X'
                            print("검색 결과: 없음 (빈 테이블)")
                    except:
                        result = 'X'
                        print("검색 결과: 없음 (resultList 없음)")
                
                df.at[idx, '현대카드_가맹여부'] = result
                print(f"최종 결과: {result}")
                
            except Exception as e:
                print(f"결과 확인 중 오류: {e}")
                df.at[idx, '현대카드_가맹여부'] = '오류: 결과 확인 실패'
                continue
            
        except Exception as e:
            print(f"전체 처리 중 오류: {e}")
            df.at[idx, '현대카드_가맹여부'] = f"오류: {str(e)[:50]}"
            continue

    # 결과 저장
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    driver.quit()
    print(f"처리 완료! 결과 파일: {output_csv}")

# 실행
if __name__ == "__main__":
    input_path = "suji.csv"
    output_path = "현대카드_가맹점_조회결과_간단버전.csv"
    search_hyundaicard_merchants(input_path, output_path)