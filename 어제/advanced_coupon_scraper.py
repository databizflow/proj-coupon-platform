from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import os
from datetime import datetime

class CouponScraper:
    def __init__(self):
        # 크롬 옵션 설정
        self.chrome_options = Options()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        # self.chrome_options.add_argument("--headless")  # 필요시 주석 해제
        
        self.driver = None
        self.wait = None
        
        # 지역 정보 (data-id와 이름 매핑)
        self.regions = {
            "1": "가평군", "2": "고양시", "3": "과천시", "5": "광명시", "6": "광주시",
            "8": "구리시", "9": "군포시", "33": "김포시", "11": "남양주시", "13": "동두천시",
            "14": "부천시", "16": "수원시", "19": "안산시", "4": "안성시", "7": "안양시",
            "10": "양주시", "12": "양평군", "15": "여주시", "17": "연천군", "18": "오산시",
            "20": "용인시", "21": "의왕시", "23": "의정부시", "25": "이천시", "28": "파주시",
            "27": "평택시", "22": "포천시", "24": "하남시", "26": "화성시"
        }
    
    def start_browser(self):
        """브라우저 시작"""
        print("브라우저 시작...")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.get("https://search.konacard.co.kr/payable-merchants")
        time.sleep(3)
    
    def select_region(self, region_id):
        """지역 선택"""
        try:
            region_name = self.regions.get(region_id, f"지역ID-{region_id}")
            print(f"{region_name} 선택 중...")
            
            # 지역 선택
            region_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"li[data-id='{region_id}']")))
            self.driver.execute_script("arguments[0].click();", region_element)
            time.sleep(1)
            print(f"{region_name} 선택 완료")
            
            # 선택 버튼 클릭
            print("선택 버튼 클릭 중...")
            try:
                select_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn_select")))
                self.driver.execute_script("arguments[0].click();", select_button)
                print("선택 버튼 클릭 완료")
                time.sleep(2)
            except Exception as select_error:
                print(f"선택 버튼 클릭 오류: {select_error}")
            
            return True
            
        except Exception as e:
            print(f"지역 선택 오류: {e}")
            return False
    
    def search_stores(self, keyword):
        """매장 검색"""
        try:
            print(f"'{keyword}' 검색 중...")
            
            # 검색어 입력
            search_input = self.wait.until(EC.element_to_be_clickable((By.NAME, "searchKey")))
            try:
                search_input.clear()
            except:
                self.driver.execute_script("arguments[0].value = '';", search_input)
            
            search_input.send_keys(keyword)
            print("검색어 입력 완료")
            
            # 검색 버튼 클릭
            search_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn_search")
            self.driver.execute_script("arguments[0].click();", search_button)
            print("검색 실행 완료")
            
            # 결과 로딩 대기
            print("검색 결과 로딩 대기 중...")
            self.wait.until(EC.visibility_of_element_located((By.ID, "table_view")))
            self.wait.until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#dataList tbody tr")) > 0)
            time.sleep(3)
            print("검색 결과 로딩 완료")
            
            return True
            
        except Exception as e:
            print(f"검색 오류: {e}")
            return False
    
    def collect_data(self, region_name, keyword):
        """데이터 수집"""
        try:
            rows = self.driver.find_elements(By.CSS_SELECTOR, "#dataList tbody tr")
            results = []
            
            print(f"총 {len(rows)}개의 매장 정보를 수집 중...")
            
            for i, row in enumerate(rows):
                try:
                    columns = row.find_elements(By.TAG_NAME, "td")
                    if len(columns) >= 4:
                        store_name = columns[0].text.strip()
                        category = columns[1].text.strip()
                        address = columns[2].text.strip()
                        phone = columns[3].text.strip()
                        
                        if store_name and "검색한 정보로" not in store_name:
                            results.append({
                                "지역": region_name,
                                "검색어": keyword,
                                "매장명": store_name,
                                "업종": category,
                                "주소": address,
                                "전화번호": phone,
                                "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            print(f"{len(results)}. {store_name} - {address}")
                except Exception as e:
                    print(f"행 {i+1} 처리 중 오류: {e}")
                    continue
            
            print(f"수집 완료: {len(results)}개 매장")
            return results
            
        except Exception as e:
            print(f"데이터 수집 오류: {e}")
            return []
    
    def save_to_csv(self, all_results, filename=None):
        """결과를 CSV 파일로 저장"""
        if not all_results:
            print("저장할 데이터가 없습니다.")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"매장검색결과_{timestamp}.csv"
        
        df = pd.DataFrame(all_results)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"결과가 '{filename}' 파일로 저장되었습니다.")
        return filename
    
    def close_browser(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            print("브라우저 종료 완료")
    
    def run_multiple_searches(self, regions_to_search, keywords_to_search):
        """여러 지역과 키워드로 자동 검색"""
        all_results = []
        
        try:
            self.start_browser()
            
            for region_id in regions_to_search:
                region_name = self.regions.get(region_id, f"지역ID-{region_id}")
                
                print(f"\n{'='*50}")
                print(f"🏢 {region_name} 검색 시작")
                print(f"{'='*50}")
                
                # 지역 선택
                if not self.select_region(region_id):
                    continue
                
                for keyword in keywords_to_search:
                    print(f"\n🔍 '{keyword}' 검색 중...")
                    
                    # 검색 실행
                    if self.search_stores(keyword):
                        # 데이터 수집
                        results = self.collect_data(region_name, keyword)
                        all_results.extend(results)
                        
                        print(f"✅ {region_name} - {keyword}: {len(results)}개 매장 수집")
                    else:
                        print(f"❌ {region_name} - {keyword}: 검색 실패")
                    
                    time.sleep(2)  # 다음 검색 전 대기
                
                # 다음 지역 검색을 위해 페이지 새로고침
                if region_id != regions_to_search[-1]:  # 마지막 지역이 아니면
                    print("다음 지역 검색을 위해 페이지 새로고침...")
                    self.driver.refresh()
                    time.sleep(3)
            
            # 결과 출력 및 저장
            if all_results:
                print(f"\n{'='*50}")
                print(f"📊 전체 수집 결과")
                print(f"{'='*50}")
                
                df = pd.DataFrame(all_results)
                print(f"총 {len(all_results)}개 매장 정보 수집 완료!")
                print("\n지역별 수집 현황:")
                print(df.groupby(['지역', '검색어']).size().to_string())
                
                # CSV 저장
                filename = self.save_to_csv(all_results)
                
                # 요약 정보 출력
                print(f"\n📋 수집 요약:")
                print(f"- 검색 지역: {len(regions_to_search)}개")
                print(f"- 검색 키워드: {len(keywords_to_search)}개")
                print(f"- 총 수집 매장: {len(all_results)}개")
                print(f"- 저장 파일: {filename}")
                
            else:
                print("수집된 데이터가 없습니다.")
                
        except Exception as e:
            print(f"전체 프로세스 오류: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.close_browser()
        
        return all_results

# 사용 예시
if __name__ == "__main__":
    scraper = CouponScraper()
    
    # 검색할 지역들 (data-id)
    regions_to_search = ["16", "14", "20"]  # 수원시, 부천시, 용인시
    
    # 검색할 키워드들
    keywords_to_search = ["올리브영", "다이소", "이디야", "BBQ"]
    
    print("🚀 다중 지역/키워드 매장 검색 시작!")
    print(f"검색 지역: {[scraper.regions[r] for r in regions_to_search]}")
    print(f"검색 키워드: {keywords_to_search}")
    
    # 검색 실행
    results = scraper.run_multiple_searches(regions_to_search, keywords_to_search)