import pandas as pd
import os

def merge_all_results():
    print("🔄 분할 처리 결과만 병합 시작!")
    print("=" * 60)
    
    # 분할 처리 결과들 읽기 (6,169개)
    print("\n📁 분할 처리 결과들 읽기...")
    all_chunks = []
    total_chunk_count = 0
    
    for i in range(1, 8):  # 1~7
        chunk_file = f'완료_분할_{i:02d}.csv'
        if os.path.exists(chunk_file):
            chunk_df = pd.read_csv(chunk_file, encoding='utf-8-sig')
            chunk_processed = chunk_df[chunk_df['현대카드_가맹여부'].notna() & (chunk_df['현대카드_가맹여부'] != '')]
            all_chunks.append(chunk_processed)
            total_chunk_count += len(chunk_processed)
            print(f"   ✅ 청크 {i}: {len(chunk_processed)}개")
        else:
            print(f"   ⚠️  청크 {i}: 파일 없음")
    
    print(f"\n📊 분할 처리 총합: {total_chunk_count}개")
    
    # 3. 분할 결과들만 병합
    print("\n🔄 분할 결과들 병합 중...")
    
    # 분할 결과들만 합치기
    merged_df = pd.concat(all_chunks, ignore_index=True)
    
    print(f"   ✅ 병합 완료: {len(merged_df)}개")
    
    # 4. 중복 제거 (혹시 있을 수 있는)
    print("\n🔍 중복 검사 및 제거...")
    before_dedup = len(merged_df)
    merged_df = merged_df.drop_duplicates(subset=['사업자등록번호', '상호명'], keep='first')
    after_dedup = len(merged_df)
    
    if before_dedup != after_dedup:
        print(f"   ⚠️  중복 제거: {before_dedup - after_dedup}개")
    else:
        print(f"   ✅ 중복 없음")
    
    # 5. 결과 통계
    print("\n📊 최종 결과 통계:")
    result_counts = merged_df['현대카드_가맹여부'].value_counts()
    
    total_processed = len(merged_df)
    for result, count in result_counts.items():
        percentage = (count / total_processed) * 100
        if result == 'O':
            print(f"   ✅ 현대카드 가맹점: {count:,}개 ({percentage:.1f}%)")
        elif result == 'X':
            print(f"   ❌ 비가맹점: {count:,}개 ({percentage:.1f}%)")
        else:
            print(f"   ⚠️  {result}: {count:,}개 ({percentage:.1f}%)")
    
    # 6. 최종 파일 저장
    output_file = '현대카드_가맹점_조회결과_최종완료.csv'
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 최종 파일 저장 완료!")
    print(f"📁 파일명: {output_file}")
    print(f"📊 총 처리 건수: {len(merged_df):,}개")
    
    # 7. 원본 데이터와 비교
    print("\n🔍 원본 데이터와 비교:")
    try:
        original_df = pd.read_csv('suji_filtered.csv', encoding='utf-8-sig')
        original_count = len(original_df)
        processed_count = len(merged_df)
        coverage = (processed_count / original_count) * 100
        
        print(f"   📋 원본 데이터: {original_count:,}개")
        print(f"   ✅ 처리 완료: {processed_count:,}개")
        print(f"   📈 처리율: {coverage:.1f}%")
        
        if coverage < 100:
            remaining = original_count - processed_count
            print(f"   ⚠️  미처리: {remaining:,}개")
    except:
        print("   ⚠️  원본 파일 비교 불가")
    
    print("\n" + "=" * 60)
    print("🎉 모든 병합 작업이 완료되었습니다!")
    print("=" * 60)
    
    return output_file

if __name__ == "__main__":
    try:
        result_file = merge_all_results()
        print(f"\n🎊 최종 결과 파일: {result_file}")
        print("📋 이제 이 파일로 현대카드 가맹점 현황을 확인할 수 있습니다!")
        
    except Exception as e:
        print(f"\n❌ 병합 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()