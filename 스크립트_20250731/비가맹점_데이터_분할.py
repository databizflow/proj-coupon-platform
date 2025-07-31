import pandas as pd
import math

def split_non_member_data():
    print("🔄 비가맹점 데이터 분할 작업 시작")
    print("=" * 50)
    
    try:
        # Excel 파일 읽기
        df = pd.read_excel('비가맹점1_정제(실행해).xlsx', sheet_name='Sheet1')
        print(f"📊 총 데이터: {len(df)}개")
        
        # 분할 개수 설정 (약 300개씩 - 더 작게 나누기)
        chunk_size = 300
        num_chunks = math.ceil(len(df) / chunk_size)
        
        print(f"\n📊 분할 계획:")
        print(f"   - 청크 크기: {chunk_size}개")
        print(f"   - 분할 개수: {num_chunks}개")
        print(f"   - 예상 완료 시간: 약 {300 * 4 / 60:.0f}분 (병렬 처리 시)")
        
        # 데이터 분할 및 저장
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, len(df))
            
            chunk_data = df.iloc[start_idx:end_idx].copy()
            chunk_filename = f'비가맹점_분할_{i+1:02d}.csv'
            
            chunk_data.to_csv(chunk_filename, index=False, encoding='utf-8-sig')
            
            print(f"   ✅ {chunk_filename}: {len(chunk_data)}개 ({start_idx+1}~{end_idx})")
        
        print(f"\n🎉 분할 완료! {num_chunks}개 파일 생성")
        print(f"\n📋 생성된 파일들:")
        for i in range(num_chunks):
            print(f"   - 비가맹점_분할_{i+1:02d}.csv")
        
        print(f"\n⚡ 병렬 처리 효과:")
        print(f"   - 단일 처리: 약 {len(df) * 4 / 60:.0f}분")
        print(f"   - {num_chunks}개 병렬: 약 {chunk_size * 4 / 60:.0f}분")
        print(f"   - 시간 단축: 약 {len(df) / chunk_size:.1f}배 빨라짐!")
        
        return num_chunks
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    split_non_member_data()