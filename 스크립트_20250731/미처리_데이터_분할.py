import pandas as pd
import math

def split_remaining_data():
    print("🔄 미처리 데이터 분할 작업 시작")
    print("=" * 50)
    
    # 현재 진행 중인 파일 읽기
    df = pd.read_csv('미처리_상호명_목록_진행중.csv', encoding='utf-8-sig')
    
    # 아직 처리되지 않은 데이터 필터링 (현대카드_가맹여부가 비어있는 것들)
    unprocessed = df[df['현대카드_가맹여부'].isna() | (df['현대카드_가맹여부'] == '')]
    
    print(f"전체 데이터: {len(df)}개")
    print(f"처리 완료: {len(df) - len(unprocessed)}개")
    print(f"미처리 데이터: {len(unprocessed)}개")
    
    if len(unprocessed) == 0:
        print("✅ 모든 데이터가 이미 처리되었습니다!")
        return
    
    # 분할 개수 설정 (약 1000개씩)
    chunk_size = 1000
    num_chunks = math.ceil(len(unprocessed) / chunk_size)
    
    print(f"\n📊 분할 계획:")
    print(f"   - 청크 크기: {chunk_size}개")
    print(f"   - 분할 개수: {num_chunks}개")
    
    # 데이터 분할 및 저장
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(unprocessed))
        
        chunk_data = unprocessed.iloc[start_idx:end_idx].copy()
        chunk_filename = f'미처리_분할_{i+1:02d}.csv'
        
        chunk_data.to_csv(chunk_filename, index=False, encoding='utf-8-sig')
        
        print(f"   ✅ {chunk_filename}: {len(chunk_data)}개 ({start_idx+1}~{end_idx})")
    
    print(f"\n🎉 분할 완료! {num_chunks}개 파일 생성")
    print("\n📋 생성된 파일들:")
    for i in range(num_chunks):
        print(f"   - 미처리_분할_{i+1:02d}.csv")
    
    return num_chunks

if __name__ == "__main__":
    split_remaining_data()