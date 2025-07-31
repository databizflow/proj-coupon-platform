import time
import pandas as pd
from datetime import datetime

def monitor_progress():
    print("🔄 현대카드 조회 진행 상황 모니터링")
    print("=" * 50)
    
    total_items = 7169
    start_time = datetime.now()
    
    while True:
        try:
            # 진행 파일 읽기
            df = pd.read_csv('미처리_상호명_목록_진행중.csv', encoding='utf-8-sig')
            
            # 처리 완료된 항목 수 계산
            processed = df['현대카드_가맹여부'].notna() & (df['현대카드_가맹여부'] != '')
            completed_count = processed.sum()
            
            # 결과별 통계
            if completed_count > 0:
                results = df[processed]['현대카드_가맹여부'].value_counts()
                o_count = results.get('O', 0)
                x_count = results.get('X', 0)
            else:
                o_count = x_count = 0
            
            # 진행률 계산
            progress_percent = (completed_count / total_items) * 100
            
            # 예상 완료 시간 계산
            elapsed_time = (datetime.now() - start_time).total_seconds()
            if completed_count > 0:
                avg_time_per_item = elapsed_time / completed_count
                remaining_items = total_items - completed_count
                estimated_remaining = remaining_items * avg_time_per_item / 3600  # 시간 단위
            else:
                estimated_remaining = 0
            
            # 화면 클리어 및 출력
            print(f"\r⏰ {datetime.now().strftime('%H:%M:%S')} | "
                  f"진행: {completed_count:,}/{total_items:,} ({progress_percent:.1f}%) | "
                  f"✅{o_count} ❌{x_count} | "
                  f"예상 완료: {estimated_remaining:.1f}시간 후", end="")
            
            time.sleep(10)  # 10초마다 업데이트
            
        except KeyboardInterrupt:
            print("\n\n모니터링을 중단합니다.")
            break
        except Exception as e:
            print(f"\n오류: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_progress()