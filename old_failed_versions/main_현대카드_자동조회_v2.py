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
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 20)

    for idx, row in df.iterrows():
        try:
            print(f"처리 중: {idx+1}/{len(df)} - {row.get('상호명', row.iloc[0])}")
            
            # 현대카드 가맹점 조회 페이지 접속
            driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
            wait.until(EC.presence_of_element_located((By.ID, "searchSido")))
            time.sleep(3)
            
            # 시도 데이터 설정 (경기도)
            setup_result = driver.execute_script("""
                try {
                    var select = document.getElementById('searchSido');
                    if (select) {
                        // 기존 옵션 제거
                        while (select.options.length > 1) {
                            select.remove(1);
                        }
                        
                        // 경기도 옵션 추가
                        var option = document.createElement('option');
                        option.value = '41';
                        option.text = '경기도';
                        select.add(option);
                        
                        return 'success';
                    } else {
                        return 'select not found';
                    }
                } catch (e) {
                    return 'error: ' + e.message;
                }
            """)
            
            if setup_result != 'success':
                print(f"시도 옵션 설정 실패: {setup_result}")
                df.at[idx, '현대카드_가맹여부'] = '오류: 시도 옵션 설정 실패'
                continue
            
            # 경기도 선택 - 더 확실한 방법
            gyeonggi_result = driver.execute_script("""
                try {
                    var select = document.getElementById('searchSido');
                    if (select) {
                        // 경기도 옵션 찾기 (더 유연하게)
                        for (var i = 0; i < select.options.length; i++) {
                            var optionText = select.options[i].text;
                            var optionValue = select.options[i].value;
                            if (optionText.includes('경기') || optionValue === '경기' || optionValue === '41') {
                                select.selectedIndex = i;
                                select.dispatchEvent(new Event('change'));
                                // 추가로 다른 이벤트들도 발생시키기
                                select.dispatchEvent(new Event('input'));
                                select.dispatchEvent(new Event('blur'));
                                return 'success: ' + optionText + ' (value: ' + optionValue + ', index: ' + i + ')';
                            }
                        }
                        
                        // 모든 옵션 확인
                        var allOptions = [];
                        for (var j = 0; j < select.options.length; j++) {
                            allOptions.push(select.options[j].text + '(' + select.options[j].value + ')');
                        }
                        return 'not found - available: ' + allOptions.join(', ');
                    } else {
                        return 'error: searchSido select not found';
                    }
                } catch (e) {
                    return 'error: ' + e.message;
                }
            """)
            
            print(f"경기도 선택 결과: {gyeonggi_result}")
            
            if not gyeonggi_result.startswith('success'):
                print(f"경기도 선택 실패: {gyeonggi_result}")
                df.at[idx, '현대카드_가맹여부'] = '오류: 경기도 선택 실패'
               
            # 시군구 옵션 로딩 대기 (더 길게)
            print("시군구 옵션 로딩 대기 중...")
            time.sleep(5)
            
            # 시군구 옵션이 로드될 때까지 반복 확인
            sigungu_result = None
            for attempt in range(10):  # 최대 10번 시도
                sigungu_result = driver.execute_script("""
                    try {
                        var select = document.getElementById('ajaxView_Sigungu');
                        if (select) {
                            var optionCount = select.options.length;
                            var optionTexts = [];
                            
                            // 모든 옵션 텍스트 수집
                            for (var i = 0; i < select.options.length; i++) {
                                var optionText = select.options[i].text;
                                optionTexts.push(optionText);
                                
                                // 용인시 수지구 찾기
                                if (optionText.includes('용인') && optionText.includes('수지')) {
                                    select.selectedIndex = i;
                                    select.dispatchEvent(new Event('change'));
                                    return 'success: ' + optionText;
                                }
                            }
                            
                            return 'not found - options: ' + optionTexts.slice(0, 5).join(', ') + '... (total: ' + optionCount + ')';
                        } else {
                            return 'error: ajaxView_Sigungu select not found';
                        }
                    } catch (e) {
                        return 'error: ' + e.message;
                    }
                """)
                
                print(f"시군구 선택 시도 {attempt + 1}: {sigungu_result}")
                
                if sigungu_result.startswith('success'):
                    break
                    
                time.sleep(2)  # 2초 더 대기 후 재시도
            
            print(f"시군구 선택 결과: {sigungu_result}")
            
            if not sigungu_result.startswith('success'):
                print(f"용인시 수지구 선택 실패: {sigungu_result}")
                df.at[idx, '현대카드_가맹여부'] = '오류: 시군구 선택 실패'
                continue  # 시군구 선택 실패시 다음 항목으로
            
            # 최종 선택 상태 확인
            final_check = driver.execute_script("""
                try {
                    var sidoSelect = document.getElementById('searchSido');
                    var sigunguSelect = document.getElementById('ajaxView_Sigungu');
                    
                    var sidoSelected = sidoSelect ? sidoSelect.options[sidoSelect.selectedIndex].text : 'none';
                    var sigunguSelected = sigunguSelect ? sigunguSelect.options[sigunguSelect.selectedIndex].text : 'none';
                    
                    return 'sido: ' + sidoSelected + ', sigungu: ' + sigunguSelected;
                } catch (e) {
                    return 'error: ' + e.message;
                }
            """)
            
            print(f"최종 선택 상태: {final_check}")
            time.sleep(2)  # 동 로딩 대기
            
            # 상호명 입력 및 검색
            store_name = row.get('상호명', row.iloc[0])
            search_result = driver.execute_script(f"""
                try {{
                    var input = document.getElementById('textMrchConmNm');
                    var button = document.getElementById('storeSearch');
                    
                    if (input && button) {{
                        input.value = '{store_name}';
                        button.click();
                        return 'success';
                    }} else {{
                        return 'elements not found';
                    }}
                }} catch (e) {{
                    return 'error: ' + e.message;
                }}
            """)
            
            if search_result != 'success':
                print(f"검색 실행 실패: {search_result}")
                df.at[idx, '현대카드_가맹여부'] = '오류: 검색 실행 실패'
                continue
                
            # 검색 결과 로딩 대기
            time.sleep(5)
            
            # 결과 판단 - HTML 구조 기반
            result_check = driver.execute_script("""
                try {
                    // 1. 먼저 "0건 검색" 메시지 확인
                    var noResultDiv = document.querySelector('.box_search_result_no');
                    if (noResultDiv && noResultDiv.style.display !== 'none') {
                        var noResultText = noResultDiv.innerText || noResultDiv.textContent;
                        if (noResultText.includes('0건이 검색되었습니다')) {
                            return {
                                hasResult: false, 
                                message: '0건 검색 결과',
                                element: 'box_search_result_no'
                            };
                        }
                    }
                    
                    // 2. 검색 결과가 있는 div 확인
                    var resultDiv = document.querySelector('.box_search_result');
                    var storeSearchList = document.getElementById('storeSearchList');
                    
                    if (resultDiv && resultDiv.style.display === 'block') {
                        // resultList tbody 확인
                        var resultList = document.getElementById('resultList');
                        if (resultList) {
                            var rows = resultList.querySelectorAll('tr');
                            if (rows.length > 0) {
                                // 첫 번째 행의 내용 확인
                                var firstRow = rows[0];
                                var cells = firstRow.querySelectorAll('td');
                                if (cells.length >= 4) {
                                    var businessType = cells[0].innerText.trim();
                                    var storeName = cells[1].innerText.trim();
                                    var address = cells[2].innerText.trim();
                                    var phone = cells[3].innerText.trim();
                                    
                                    if (businessType && storeName && address) {
                                        return {
                                            hasResult: true,
                                            message: 'result_found',
                                            element: 'resultList',
                                            data: {
                                                businessType: businessType,
                                                storeName: storeName,
                                                address: address,
                                                phone: phone
                                            }
                                        };
                                    }
                                }
                            }
                        }
                    }
                    
                    // 3. 기본적으로 결과 없음으로 판단
                    return {
                        hasResult: false,
                        message: 'no_result_element_found',
                        element: 'none'
                    };
                    
                } catch (e) {
                    return {
                        hasResult: false, 
                        message: 'error: ' + e.message,
                        element: 'error'
                    };
                }
            """)
            
            has_result = result_check.get('hasResult', False)
            check_message = result_check.get('message', 'unknown')
            element_type = result_check.get('element', 'unknown')
            
            print(f"결과 확인: {check_message} (요소: {element_type})")
            
            # 결과가 있는 경우 상세 정보 출력
            if has_result and 'data' in result_check:
                data = result_check['data']
                print(f"  업종: {data.get('businessType', '')}")
                print(f"  가맹점: {data.get('storeName', '')}")
                print(f"  주소: {data.get('address', '')[:50]}...")
                print(f"  전화: {data.get('phone', '')}")
            
            df.at[idx, '현대카드_가맹여부'] = 'O' if has_result else 'X'
            print(f"최종 결과: {'O' if has_result else 'X'}")
            
        except Exception as e:
            print(f"오류 발생: {e}")
            df.at[idx, '현대카드_가맹여부'] = f"오류: {str(e)[:50]}"
            continue

    # 결과 저장
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    driver.quit()
    print(f"처리 완료! 결과 파일: {output_csv}")

# 실행
if __name__ == "__main__":
    input_path = "suji.csv"
    output_path = "현대카드_가맹점_조회결과_v2.csv"
    search_hyundaicard_merchants(input_path, output_path)