import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HyundaiCardChecker:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.setup_driver()
    
    def setup_driver(self):
        """Chrome WebDriver 설정 (개선된 버전)"""
        chrome_options = Options()
        
        # 기본 설정
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        
        # 로그 레벨 설정 (에러 메시지 줄이기)
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 봇 탐지 우회 설정
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # User-Agent 설정
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
        
        # 프로파일 설정
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins-discovery')
        chrome_options.add_argument('--disable-default-apps')
        
        try:
            # 기본 방식으로 Chrome WebDriver 초기화
            logger.info("Chrome WebDriver 초기화 시작")
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome WebDriver 초기화 완료")
            
            # WebDriver 속성 숨기기
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 대기 시간 설정
            self.wait = WebDriverWait(self.driver, 30)
            self.driver.implicitly_wait(10)
            
            logger.info("WebDriver 설정 완료")
            
        except Exception as e:
            logger.error(f"WebDriver 초기화 실패: {e}")
            logger.info("ChromeDriver 설치 확인이 필요합니다.")
            logger.info("해결 방법:")
            logger.info("1. pip install webdriver-manager")
            logger.info("2. 또는 ChromeDriver를 수동으로 다운로드하여 PATH에 추가")
            raise
    
    def navigate_to_site(self):
        """현대카드 가맹점 검색 페이지로 이동 및 지역 설정"""
        try:
            url = "https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc"
            logger.info(f"사이트 접속 중: {url}")
            self.driver.get(url)
            
            # 페이지 로딩 대기
            time.sleep(5)
            
            # 지역 선택 과정
            if not self.setup_region():
                return False
            
            logger.info("페이지 로딩 완료 및 지역 설정 완료")
            return True
                
        except Exception as e:
            logger.error(f"사이트 접속 실패: {e}")
            return False
    
    def setup_region(self):
        """지역 설정: 경기 > 용인시 수지구 (단순화된 버전)"""
        try:
            logger.info("지역 설정 시작")
            
            # 페이지 로딩 완료 대기
            time.sleep(5)
            
            # 현재 페이지의 select 요소들 확인
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            logger.info(f"페이지에서 발견된 select 요소 개수: {len(selects)}")
            
            if len(selects) < 2:
                logger.error("필요한 select 요소를 찾을 수 없습니다")
                return False
            
            try:
                # 1단계: 시도 선택 (경기)
                sido_select = selects[0]
                logger.info("시도 선택 시작")
                
                # 경기도 옵션 찾기 및 선택
                gyeonggi_selected = self.driver.execute_script("""
                    var select = arguments[0];
                    var options = select.options;
                    for (var i = 0; i < options.length; i++) {
                        if (options[i].text.indexOf('경기') !== -1) {
                            select.selectedIndex = i;
                            select.value = options[i].value;
                            
                            // change 이벤트 발생
                            var event = new Event('change', { bubbles: true });
                            select.dispatchEvent(event);
                            
                            console.log('경기도 선택됨:', options[i].text);
                            return options[i].text;
                        }
                    }
                    return null;
                """, sido_select)
                
                if gyeonggi_selected:
                    logger.info(f"경기도 선택 성공: {gyeonggi_selected}")
                else:
                    logger.warning("경기도 옵션을 찾을 수 없음")
                
                # 시군구 로딩 대기
                time.sleep(4)
                
            except Exception as e:
                logger.warning(f"경기도 선택 중 오류: {e}")
            
            try:
                # 2단계: 시군구 선택 (용인시 수지구)
                # select 요소를 다시 찾기 (DOM이 업데이트되었을 수 있음)
                selects = self.driver.find_elements(By.TAG_NAME, "select")
                if len(selects) >= 2:
                    sigungu_select = selects[1]
                    logger.info("시군구 선택 시작")
                    
                    suji_selected = self.driver.execute_script("""
                        var select = arguments[0];
                        var options = select.options;
                        for (var i = 0; i < options.length; i++) {
                            var text = options[i].text;
                            if (text.indexOf('용인시') !== -1 && text.indexOf('수지구') !== -1) {
                                select.selectedIndex = i;
                                select.value = options[i].value;
                                
                                // change 이벤트 발생
                                var event = new Event('change', { bubbles: true });
                                select.dispatchEvent(event);
                                
                                console.log('용인시 수지구 선택됨:', text);
                                return text;
                            }
                        }
                        return null;
                    """, sigungu_select)
                    
                    if suji_selected:
                        logger.info(f"용인시 수지구 선택 성공: {suji_selected}")
                    else:
                        logger.error("용인시 수지구 옵션을 찾을 수 없음")
                        return False
                    
                    # 읍면동 로딩 대기
                    time.sleep(4)
                    
            except Exception as e:
                logger.error(f"용인시 수지구 선택 중 오류: {e}")
                return False
            
            # 읍면동은 선택하지 않고 바로 검색 필드 확인
            logger.info("읍면동 선택 생략 - 바로 검색 진행")
            time.sleep(2)
            
            try:
                search_input = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "textMrchConmNm"))
                )
                logger.info("검색 필드 활성화 확인 완료")
                
                # 현재 선택 상태 로그
                logger.info("지역 설정 완료 - 검색 준비됨")
                return True
                
            except TimeoutException:
                logger.error("검색 필드가 활성화되지 않음")
                # 디버깅을 위해 현재 페이지 상태 저장
                self.save_debug_info()
                return False
                
        except Exception as e:
            logger.error(f"지역 설정 중 심각한 오류: {e}")
            return False
    


    def search_store(self, store_name):
        """상호명으로 가맹점 검색"""
        try:
            logger.info(f"'{store_name}' 검색 시작")
            
            # 검색 필드 클리어 및 입력
            search_input = self.driver.find_element(By.ID, "textMrchConmNm")
            search_input.clear()
            time.sleep(0.5)
            search_input.send_keys(store_name)
            logger.info(f"검색어 입력 완료: {store_name}")
            
            # 검색 버튼 클릭
            search_button = self.driver.find_element(By.ID, "storeSearch")
            search_button.click()
            logger.info("검색 버튼 클릭")
            
            # 검색 결과 로딩 대기
            time.sleep(4)
            
            # 결과 확인
            result = self.check_search_results()
            logger.info(f"'{store_name}' 검색 결과: {result}")
            return result
            
        except Exception as e:
            logger.error(f"'{store_name}' 검색 중 오류: {e}")
            return "오류"
    
    def check_search_results(self):
        """검색 결과 확인 (정확한 패턴 기반)"""
        try:
            # 페이지 소스 가져오기
            page_source = self.driver.page_source
            
            # 검색어 가져오기
            search_input = self.driver.find_element(By.ID, "textMrchConmNm")
            searched_name = search_input.get_attribute("value")
            
            logger.info(f"검색어: '{searched_name}' 결과 확인 중...")
            
            if searched_name:
                # 방법 1: 정확한 결과 메시지 패턴 확인
                result_success_pattern = f"{searched_name}</span>상호 검색 결과입니다"
                result_fail_pattern = f"{searched_name}</span>상호 검색 결과가 없습니다"
                
                if result_success_pattern in page_source:
                    logger.info(f"검색 결과 있음 - 성공 패턴 발견: '{searched_name}상호 검색 결과입니다'")
                    return "O"
                elif result_fail_pattern in page_source:
                    logger.info(f"검색 결과 없음 - 실패 패턴 발견: '{searched_name}상호 검색 결과가 없습니다'")
                    return "X"
                
                # 방법 2: 대체 패턴 확인 (span 태그 없이)
                alt_success_pattern = f"{searched_name}상호 검색 결과입니다"
                alt_fail_pattern = f"{searched_name}상호 검색 결과가 없습니다"
                
                if alt_success_pattern in page_source:
                    logger.info(f"검색 결과 있음 - 대체 성공 패턴 발견")
                    
                    # 추가: 결과 개수 확인
                    try:
                        result_list = self.driver.find_element(By.ID, "resultList")
                        rows = result_list.find_elements(By.TAG_NAME, "tr")
                        logger.info(f"검색 결과 개수: {len(rows)}개")
                    except:
                        logger.info("결과 개수 확인 실패")
                    
                    return "O"
                elif alt_fail_pattern in page_source:
                    logger.info(f"검색 결과 없음 - 대체 실패 패턴 발견")
                    return "X"
            
            # 방법 2: resultList 확인
            try:
                result_list = self.driver.find_element(By.ID, "resultList")
                rows = result_list.find_elements(By.TAG_NAME, "tr")
                
                if len(rows) > 0:
                    # 첫 번째 행에 실제 데이터가 있는지 확인
                    first_row = rows[0]
                    cells = first_row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cells) >= 2 and cells[1].text.strip():
                        logger.info(f"검색 결과 발견: {cells[1].text}")
                        return "O"
                
            except Exception as e:
                logger.warning(f"resultList 확인 중 오류: {e}")
            
            # 방법 3: storeSearchList div 확인
            try:
                search_list = self.driver.find_element(By.ID, "storeSearchList")
                display_style = search_list.get_attribute("style")
                
                if "display: block" in display_style:
                    # 내부에 실제 내용이 있는지 확인
                    if search_list.text.strip() and "업종" in search_list.text:
                        logger.info("검색 결과 발견 (storeSearchList)")
                        return "O"
                        
            except Exception as e:
                logger.warning(f"storeSearchList 확인 중 오류: {e}")
            
            # 모든 방법으로 결과를 찾지 못한 경우
            logger.info("검색 결과 없음")
            return "X"
            
        except Exception as e:
            logger.error(f"결과 확인 중 오류: {e}")
            return "오류"
    
    def close(self):
        """WebDriver 종료"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver 종료 완료")
            except Exception as e:
                logger.warning(f"WebDriver 종료 중 오류: {e}")
            finally:
                self.driver = None
    


# 간단한 테스트 함수
def test_single_search():
    """단일 검색 테스트"""
    checker = HyundaiCardChecker()
    
    try:
        if checker.navigate_to_site():
            # 테스트 상호명들
            test_stores = ["효티네일", "BBQ", "올리브영", "스타벅스", "존재하지않는상호명123"]
            
            for store in test_stores:
                print(f"\n=== {store} 검색 테스트 ===")
                result = checker.search_store(store)
                print(f"결과: {result}")
                time.sleep(2)
    finally:
        checker.close()
    
    def log_current_region(self):
        """현재 선택된 지역 정보 로그"""
        try:
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            if len(selects) >= 2:
                sido_text = selects[0].find_element(By.CSS_SELECTOR, "option:checked").text
                sigungu_text = selects[1].find_element(By.CSS_SELECTOR, "option:checked").text
                logger.info(f"현재 선택된 지역: {sido_text} > {sigungu_text}")
        except Exception as e:
            logger.warning(f"지역 정보 로그 실패: {e}")

    def search_store(self, store_name):
        """상호명으로 가맹점 검색"""
        try:
            # 검색 필드 클리어 및 입력
            search_input = self.driver.find_element(By.ID, "textMrchConmNm")
            search_input.clear()
            time.sleep(0.5)
            search_input.send_keys(store_name)
            
            # 검색 버튼 클릭
            search_button = self.driver.find_element(By.ID, "storeSearch")
            search_button.click()
            
            # 검색 결과 로딩 대기 (최대 10초)
            time.sleep(4)
            
            # 결과 확인을 위한 여러 방법 시도
            return self.check_search_results()
            
        except Exception as e:
            logger.error(f"검색 중 오류 발생: {e}")
            return "오류"
    
    def check_search_results(self):
        """검색 결과 확인 (여러 방법으로 시도)"""
        try:
            # 방법 1: resultList tbody 확인
            try:
                result_tbody = self.wait.until(
                    EC.presence_of_element_located((By.ID, "resultList"))
                )
                
                # tbody 내부에 tr 요소가 있는지 확인
                rows = result_tbody.find_elements(By.TAG_NAME, "tr")
                if len(rows) > 0:
                    # tr 내부에 실제 데이터가 있는지 확인
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) > 0 and cells[0].text.strip():
                            logger.info("검색 결과 발견 (방법 1)")
                            return "O"
                
            except TimeoutException:
                pass
            
            # 방법 2: storeSearchList div의 display 상태 확인
            try:
                search_list_div = self.driver.find_element(By.ID, "storeSearchList")
                display_style = search_list_div.get_attribute("style")
                
                if "display: block" in display_style or "display:block" in display_style:
                    # 내부에 실제 결과가 있는지 재확인
                    result_tbody = search_list_div.find_element(By.ID, "resultList")
                    if result_tbody.text.strip():
                        logger.info("검색 결과 발견 (방법 2)")
                        return "O"
                        
            except NoSuchElementException:
                pass
            
            # 방법 3: 페이지 전체 텍스트에서 "총 0건" 메시지 확인
            page_text = self.driver.page_source
            if "총 0건이 검색되었습니다" in page_text:
                logger.info("검색 결과 없음 (총 0건 메시지 발견)")
                return "X"
            
            # 방법 4: JavaScript로 결과 확인
            try:
                result = self.driver.execute_script("""
                    var resultList = document.getElementById('resultList');
                    if (resultList) {
                        var rows = resultList.getElementsByTagName('tr');
                        for (var i = 0; i < rows.length; i++) {
                            var cells = rows[i].getElementsByTagName('td');
                            if (cells.length > 0 && cells[0].innerText.trim()) {
                                return 'found';
                            }
                        }
                    }
                    return 'not_found';
                """)
                
                if result == 'found':
                    logger.info("검색 결과 발견 (JavaScript 방법)")
                    return "O"
                    
            except Exception as js_error:
                logger.warning(f"JavaScript 실행 오류: {js_error}")
            
            # 모든 방법으로 결과를 찾지 못한 경우
            logger.info("모든 방법으로 검색 결과를 확인했지만 결과 없음")
            return "X"
            
        except Exception as e:
            logger.error(f"결과 확인 중 오류: {e}")
            return "오류"
    
    def process_csv(self, input_file="suji_filtered.csv", output_file="suji_filtered_result.csv"):
        """CSV 파일 처리"""
        try:
            # CSV 파일 읽기
            df = pd.read_csv(input_file, encoding='utf-8-sig')
            logger.info(f"CSV 파일 로드 완료: {len(df)}개 항목")
            
            # 결과 컬럼 추가
            df['현대카드_가맹여부'] = ''
            
            # 현대카드 사이트로 이동
            if not self.navigate_to_site():
                logger.error("사이트 접속 실패")
                return
            
            # 각 상호명에 대해 검색 수행
            for index, row in df.iterrows():
                store_name = str(row['상호명']).strip()
                
                if not store_name or store_name == 'nan':
                    df.at[index, '현대카드_가맹여부'] = '오류'
                    continue
                
                logger.info(f"[{index+1}/{len(df)}] 검색 중: {store_name}")
                
                # 검색 수행
                result = self.search_store(store_name)
                df.at[index, '현대카드_가맹여부'] = result
                
                logger.info(f"결과: {result}")
                
                # 요청 간격 (봇 탐지 방지)
                sleep_time = random.uniform(1.5, 3.5)
                time.sleep(sleep_time)
                
                # 중간 저장 (100개마다)
                if (index + 1) % 100 == 0:
                    df.to_csv(output_file, index=False, encoding='utf-8-sig')
                    logger.info(f"중간 저장 완료: {index + 1}개 처리")
            
            # 최종 저장
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            logger.info(f"처리 완료! 결과 파일: {output_file}")
            
            # 결과 통계
            result_counts = df['현대카드_가맹여부'].value_counts()
            logger.info(f"결과 통계:\n{result_counts}")
            
        except Exception as e:
            logger.error(f"CSV 처리 중 오류: {e}")
        finally:
            self.close()
    
    def close(self):
        """WebDriver 종료"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver 종료 완료")
            except Exception as e:
                logger.warning(f"WebDriver 종료 중 오류: {e}")
            finally:
                self.driver = None

# 테스트 함수
def test_single_search():
    """단일 검색 테스트"""
    checker = HyundaiCardChecker()
    
    try:
        if checker.navigate_to_site():
            # 테스트 상호명들
            test_stores = ["효티네일", "BBQ", "올리브영", "스타벅스", "존재하지않는상호명123"]
            
            for store in test_stores:
                print(f"\n=== {store} 검색 테스트 ===")
                result = checker.search_store(store)
                print(f"결과: {result}")
                time.sleep(2)
    finally:
        checker.close()

# 메인 실행
def main():
    """메인 함수"""
    print("현대카드 가맹점 자동 조회 스크립트")
    print("1. 단일 검색 테스트")
    print("2. CSV 파일 전체 처리")
    
    choice = input("선택하세요 (1 또는 2): ").strip()
    
    if choice == "1":
        test_single_search()
    elif choice == "2":
        checker = HyundaiCardChecker()
        checker.process_csv()
    else:
        print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()