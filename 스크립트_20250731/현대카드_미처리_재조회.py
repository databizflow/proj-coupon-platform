"""
현대카드 가맹점 미처리 데이터 재조회 프로그램
"""

import os
import sys
import pandas as pd
from hyundaicard_checker import HyundaiCardChecker
import logging
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('현대카드_재조회_로그.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def process_remaining_stores():
    """미처리 상호명들 재조회"""
    try:
        print("🔄 현대카드 가맹점 미처리 데이터 재조회 시작!")
        print("-" * 60)
        
        # 미처리 데이터 읽기
        df = pd.read_csv('미처리_상호명_목록.csv', encoding='utf-8-sig')
        print(f"📊 미처리 데이터: {len(df)}개")
        
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
            store_name = str(row['상호명']).strip()
            
            if not store_name or store_name == 'nan':
                df.at[index, '현대카드_가맹여부'] = '오류'
                error_count += 1
                continue
            
            print(f"\n🔍 [{index+1}/{len(df)}] 검색 중: {store_name}")
            
            try:
                # 검색 수행
                result = checker.search_store(store_name)
                df.at[index, '현대카드_가맹여부'] = result
                
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
                
                print(f"📊 진행률: {progress:.1f}% ({success_count}개 성공, {error_count}개 오류)")
                print(f"⏱️  예상 남은 시간: {estimated_remaining_time/60:.1f}분")
                
                # 중간 저장 (50개마다)
                if (index + 1) % 50 == 0:
                    df.to_csv('미처리_상호명_목록_진행중.csv', index=False, encoding='utf-8-sig')
                    print(f"💾 중간 저장 완료: {index + 1}개 처리")
                
            except Exception as e:
                print(f"❌ 검색 오류: {e}")
                df.at[index, '현대카드_가맹여부'] = '오류'
                error_count += 1
        
        # 최종 저장
        df.to_csv('미처리_상호명_목록_완료.csv', index=False, encoding='utf-8-sig')
        
        # 결과 통계
        result_counts = df['현대카드_가맹여부'].value_counts()
        
        print("\n" + "=" * 60)
        print("🎉 재조회 작업 완료!")
        print("=" * 60)
        print(f"📁 결과 파일: 미처리_상호명_목록_완료.csv")
        print(f"📊 재조회 결과:")
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
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 처리 중 오류 발생: {e}")
        return False
    
    finally:
        # WebDriver 종료
        try:
            checker.close()
            print("🔒 브라우저 종료 완료")
        except:
            pass

def merge_results():
    """원본 데이터와 재조회 결과 병합"""
    try:
        print("\n🔄 결과 병합 중...")
        
        # 원본 완료 데이터 읽기
        original_df = pd.read_csv('현대카드_가맹점_조회결과_완료.csv', encoding='utf-8-sig')
        
        # 재조회 완료 데이터 읽기
        reprocessed_df = pd.read_csv('미처리_상호명_목록_완료.csv', encoding='utf-8-sig')
        
        # 재조회된 데이터로 원본 업데이트
        for index, row in reprocessed_df.iterrows():
            # 상호명과 사업자등록번호로 매칭하여 업데이트
            mask = (original_df['상호명'] == row['상호명']) & (original_df['사업자등록번호'] == row['사업자등록번호'])
            original_df.loc[mask, '현대카드_가맹여부'] = row['현대카드_가맹여부']
        
        # 최종 결과 저장
        original_df.to_csv('현대카드_가맹점_조회결과_최종.csv', index=False, encoding='utf-8-sig')
        
        # 최종 통계
        final_counts = original_df['현대카드_가맹여부'].value_counts()
        
        print("\n" + "=" * 60)
        print("🎊 최종 결과 통계")
        print("=" * 60)
        print(f"📁 최종 파일: 현대카드_가맹점_조회결과_최종.csv")
        print(f"📊 전체 {len(original_df)}개 상호명 중:")
        
        for result, count in final_counts.items():
            if result == 'O':
                print(f"   ✅ 현대카드 가맹점: {count}개 ({count/len(original_df)*100:.1f}%)")
            elif result == 'X':
                print(f"   ❌ 비가맹점: {count}개 ({count/len(original_df)*100:.1f}%)")
            elif pd.isna(result) or result == '':
                print(f"   ⚠️  미처리: {count}개 ({count/len(original_df)*100:.1f}%)")
            else:
                print(f"   ⚠️  {result}: {count}개 ({count/len(original_df)*100:.1f}%)")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 결과 병합 중 오류: {e}")

if __name__ == "__main__":
    try:
        # 미처리 데이터 재조회
        success = process_remaining_stores()
        
        if success:
            # 결과 병합
            merge_results()
            print(f"\n🎊 모든 작업이 완료되었습니다!")
        else:
            print(f"\n💥 재조회 작업 중 오류가 발생했습니다.")
        
        input("\n⏎ Enter를 눌러 종료...")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
        input("⏎ Enter를 눌러 종료...")