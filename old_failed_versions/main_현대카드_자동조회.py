
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
            
            driver.get("https://www.hyundaicard.com/cpb/gs/CPBGS2005_01.hc")
            wait.until(EC.presence_of_element_located((By.ID, "searchSido")))
            time.sleep(5)  # 페이지 완전 로딩 대기
            
            # JavaScript로 시도 데이터 직접 추가
            setup_result = driver.execute_script("""
                try {
                    var sidoData = [
                        {code: '11', name: '서울특별시'},
                        {code: '26', name: '부산광역시'},
                        {code: '27', name: '대구광역시'},
                        {code: '28', name: '인천광역시'},
                        {code: '29', name: '광주광역시'},
                        {code: '30', name: '대전광역시'},
                        {code: '31', name: '울산광역시'},
                        {code: '36', name: '세종특별자치시'},
                        {code: '41', name: '경기도'},
                        {code: '42', name: '강원특별자치도'},
                        {code: '43', name: '충청북도'},
                        {code: '44', name: '충청남도'},
                        {code: '45', name: '전북특별자치도'},
                        {code: '46', name: '전라남도'},
                        {code: '47', name: '경상북도'},
                        {code: '48', name: '경상남도'},
                        {code: '50', name: '제주특별자치도'}
                    ];
                    
                    var select = document.getElementById('searchSido');
                    if (select) {
                        while (select.options.length > 1) {
                            select.remove(1);
                        }
                        
                        sidoData.forEach(function(item) {
                            var option = document.createElement('option');
                            option.value = item.code;
                            option.text = item.name;
                            select.add(option);
                        });
                        
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
            
            # 경기도 선택
            gyeonggi_result = driver.execute_script("""
                var select = document.getElementById('searchSido');
                for(var i = 0; i < select.options.length; i++) {
                    if(select.options[i].text.includes('경기')) {
                        select.selectedIndex = i;
                        select.dispatchEvent(new Event('change'));
                        return 'success';
                    }
                }
                return 'not found';
            """)
            
            if gyeonggi_result != 'success':
                print("경기도 선택 실패")
                df.at[idx, '현대카드_가맹여부'] = '오류: 경기도 선택 실패'
                continue
            
            time.sleep(3)  # 시군구 로딩 대기
            
            # 시군구는 선택하지 않고 바로 검색 (전체 경기도에서 검색)

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
                
            time.sleep(8)  # 검색 결과 로딩 대기 (더 길게)

            # 간단한 요소값 기반 결과 판단
            result_check = driver.execute_script("""
                try {
                    var pageText = document.body.innerText;
                    
                    // "결과 없음" 메시지 패턴 확인
                    var noResultPatterns = [
                        "검색 결과가 없습니다",
                        "검색결과가 없습니다", 
                        "조회된 결과가 없습니다",
                        "결과가 없습니다",
                        "검색된 가맹점이 없습니다",
                        "가맹점이 없습니다",
                        "총 0건이 검색되었습니다",
                        "0건이 검색되었습니다"
                    ];
                    
                    // 결과 없음 메시지가 있으면 바로 false
                    for (var i = 0; i < noResultPatterns.length; i++) {
                        if (pageText.includes(noResultPatterns[i])) {
                            return {hasResult: false, message: noResultPatterns[i]};
                        }
                    }
                    
                    // "0건" 패턴 확인
                    if (pageText.match(/총\s*0\s*건/) || pageText.match(/0\s*건이\s*검색/)) {
                        return {hasResult: false, message: '0건 검색 결과'};
                    }
                    
                    // 결과가 있을 때의 키워드 조합 확인
                    var hasAllKeywords = pageText.includes('업종') && 
                                        pageText.includes('가맹점') && 
                                        pageText.includes('주소') &&
                                        pageText.includes('전화번호');
                    
                    // 실제 가맹점 데이터 키워드 확인 (편의점, 음식점, 카페 등)
                    var hasBusinessTypes = pageText.includes('편의점') || 
                                          pageText.includes('음식점') || 
                                          pageText.includes('카페') || 
                                          pageText.includes('마트') || 
                                          pageText.includes('약국') ||
                                          pageText.includes('병원') ||
                                          pageText.includes('미용');
                    
                    // 전화번호 패턴 확인 (031-xxx-xxxx 형태)
                    var hasPhoneNumber = pageText.match(/\d{2,3}-\d{3,4}-\d{4}/);
                    
                    return {
                        hasResult: hasAllKeywords && (hasBusinessTypes || hasPhoneNumber),
                        message: hasAllKeywords ? (hasBusinessTypes ? 'business_type_found' : (hasPhoneNumber ? 'phone_found' : 'keywords_only')) : 'no_keywords',
                        hasAllKeywords: hasAllKeywords,
                        hasBusinessTypes: hasBusinessTypes,
                        hasPhoneNumber: !!hasPhoneNumber,
                        pageTextSample: pageText.substring(0, 300)
                    };
                    
                } catch (e) {
                    return {hasResult: false, message: 'error: ' + e.message};
                }
            """)
            
            has_result = result_check.get('hasResult', False)
            check_message = result_check.get('message', 'unknown')
            
            print(f"결과 확인: {check_message}")
            print(f"모든 키워드: {result_check.get('hasAllKeywords', False)}")
            print(f"업종 키워드: {result_check.get('hasBusinessTypes', False)}")
            print(f"전화번호: {result_check.get('hasPhoneNumber', False)}")
            
            if result_check.get('pageTextSample'):
                print(f"페이지 텍스트 샘플: {result_check['pageTextSample'][:150]}...")
            
            df.at[idx, '현대카드_가맹여부'] = 'O' if has_result else 'X'
            print(f"최종 결과: {'O' if has_result else 'X'}")
            
        except Exception as e:
            print(f"오류 발생: {e}")
            df.at[idx, '현대카드_가맹여부'] = f"오류: {str(e)[:50]}"
            continue

    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    driver.quit()

# 실행 예시
if __name__ == "__main__":
    input_path = "suji.csv"
    output_path = "현대카드_가맹점_조회결과.csv"
    search_hyundaicard_merchants(input_path, output_path)
