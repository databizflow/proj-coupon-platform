"""
비가맹점 현대카드 분할 처리기
특정 분할 파일을 처리하는 스크립트
"""

import os
import sys
import pandas as pd
from hyundaicard_checker import HyundaiCardChecker
import logging
import time
from datetime import datetime

def process_chunk_file(chunk_number):
    """특정 청크 파일 처리"""
    
    # 파일명 설정
    input_file = f'비가맹점_분할_{chunk_number:02d}.csv'
    output_file = f'비가맹점_완료_{chunk_number:02d}.csv'
    log_file = f'비가맹점_로그_{chunk_number:02d}.log'
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        print(f"🚀 비가맹점 청크 {chunk_number} 처리 시작!")
        print(f"📁 입력 파일: {input_file}")
        print(f"📁 출력 파일: {output_file}")
        print("-" * 60)
        
        # 입력 파일 확인
        if not os.path.exists(input_file):
            print(f"❌ 오류: '{input_file}' 파일을 찾을 수 없습니다.")
            return False
        
        # 데이터 읽기
        df = pd.read_csv(input_file, encoding='utf-8-sig')
        print(f"📊 처리할 데이터: {len(df)}개")
        
        # 현대카드_가맹여부_재검토 컬럼 추가
        df['현대카드_가맹여부_재검토'] = ''
        
        # HyundaiCardChecker 인스턴스 생성
        checker = HyundaiCardChecker()
        
        # 웹사이트 접속 및 지역 설정
        print("🌐 현대카드 웹사이트 접속 중...")
        if not checker.navigate_to_site():
            print("❌ 웹사이트 접속 실패")
            return False
        
        print("✅ 웹사이트 접속 및 지역 설정 완료")
        print("📍 지역: 경기도 용인시 수지구")
        
        # 각 상호명 검색
        success_count = 0
        error_count = 0
        start_time = time.time()
        
        for index, row in df.iterrows():
            # 상호명 컬럼 찾기
            store_name = None
            possible_columns = ['상호명', '업체명', '가맹점명', '점포명', 'name', '상호']
            
            for col in possible_columns:
                if col in df.columns:
                    store_name = str(row[col]).strip()
                    break
            
            if not store_name or store_name == 'nan':
                df.at[index, '현대카드_가맹여부_재검토'] = '오류'
                error_count += 1
                continue
            
            print(f"\n🔍 청크{chunk_number} [{index+1}/{len(df)}] 검색 중: {store_name}")
            
            try:
                # 검색 수행
                result = checker.search_store(store_name)
                df.at[index, '현대카드_가맹여부_재검토'] = result
                
                # 결과 표시
                if result == 'O':
                    print(f"✅ 결과: 가맹점 발견")
                elif result == 'X':
                    print(f"❌ 결과: 가맹점 없음")
                else:
                    print(f"⚠️  결과: {result}")
                    error_count += 1
                    continue
                
                success_count += 1
                
                # 진행률 및 예상 시간 표시
                progress = (index + 1) / len(df) * 100
                elapsed_time = time.time() - start_time
                avg_time_per_item = elapsed_time / (index + 1)
                remaining_items = len(df) - (index + 1)
                estimated_remaining_time = remaining_items * avg_time_per_item
                
                print(f"📊 청크{chunk_number} 진행률: {progress:.1f}% ({success_count}개 성공, {error_count}개 오류)")
                print(f"⏱️  예상 남은 시간: {estimated_remaining_time/60:.1f}분")
                
                # 중간 저장 (50개마다)
                if (index + 1) % 50 == 0:
                    df.to_csv(output_file, index=False, encoding='utf-8-sig')
                    print(f"💾 중간 저장 완료: {index + 1}개 처리")
                
            except Exception as e:
                print(f"❌ 검색 오류: {e}")
                df.at[index, '현대카드_가맹여부_재검토'] = '오류'
                error_count += 1
        
        # 최종 저장
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # 결과 통계
        result_counts = df['현대카드_가맹여부_재검토'].value_counts()
        
        print("\n" + "=" * 60)
        print(f"🎉 청크 {chunk_number} 작업 완료!")
        print("=" * 60)
        print(f"📁 결과 파일: {output_file}")
        print(f"📊 처리 결과:")
        for result, count in result_counts.items():
            if result == 'O':
                print(f"   ✅ 가맹점: {count}개")
            elif result == 'X':
                print(f"   ❌ 비가맹점: {count}개")
            else:
                print(f"   ⚠️  {result}: {count}개")
        
        total_time = time.time() - start_time
        print(f"⏱️  총 소요 시간: {total_time/60:.1f}분")
        print(f"📈 성공률: {success_count}/{len(df)} ({success_count/len(df)*100:.1f}%)")
        
        # 가맹점 발견율
        if 'O' in result_counts:
            discovery_rate = result_counts['O'] / len(df) * 100
            print(f"🎯 가맹점 발견율: {discovery_rate:.1f}%")
        
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 처리 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # WebDriver 종료
        try:
            checker.close()
            print("🔒 브라우저 종료 완료")
        except:
            pass

def main():
    """메인 함수"""
    if len(sys.argv) != 2:
        print("사용법: python 비가맹점_분할_처리기.py [청크번호]")
        print("예시: python 비가맹점_분할_처리기.py 1")
        print("청크번호: 1~6")
        return
    
    try:
        chunk_number = int(sys.argv[1])
        if chunk_number < 1 or chunk_number > 6:
            print("❌ 청크번호는 1~6 사이여야 합니다.")
            return
        
        success = process_chunk_file(chunk_number)
        
        if success:
            print(f"\n🎊 청크 {chunk_number} 처리가 완료되었습니다!")
        else:
            print(f"\n💥 청크 {chunk_number} 처리 중 오류가 발생했습니다.")
        
    except ValueError:
        print("❌ 청크번호는 숫자여야 합니다.")
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")

if __name__ == "__main__":
    main()