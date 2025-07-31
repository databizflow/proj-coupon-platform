import pandas as pd

def extract_non_members():
    print("🔍 현대카드 비가맹점 추출 시작!")
    print("=" * 50)
    
    try:
        # 최종 완료 파일 읽기
        df = pd.read_csv('현대카드_가맹점_조회결과_최종완료.csv', encoding='utf-8-sig')
        print(f"📊 전체 데이터: {len(df)}개")
        
        # 현대카드 사용여부가 'X'인 항목들만 필터링
        non_members = df[df['현대카드_가맹여부'] == 'X'].copy()
        print(f"❌ 비가맹점: {len(non_members)}개")
        
        if len(non_members) == 0:
            print("⚠️  비가맹점 데이터가 없습니다.")
            return
        
        # Excel 파일로 저장 (두 개 시트)
        output_file = '현대카드_가맹점_분석결과.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 첫 번째 시트: 전체 결과
            df.to_excel(writer, sheet_name='전체결과', index=False)
            print(f"✅ '전체결과' 시트: {len(df)}개")
            
            # 두 번째 시트: 비가맹점만
            non_members.to_excel(writer, sheet_name='비가맹점', index=False)
            print(f"❌ '비가맹점' 시트: {len(non_members)}개")
        
        print(f"\n💾 Excel 파일 저장 완료!")
        print(f"📁 파일명: {output_file}")
        
        # 비가맹점 통계
        print(f"\n📊 비가맹점 상세 정보:")
        print(f"   - 총 비가맹점: {len(non_members)}개")
        print(f"   - 전체 대비: {len(non_members)/len(df)*100:.1f}%")
        
        # 업종별 비가맹점 현황 (상위 10개)
        if '업종명(종목명)' in non_members.columns:
            print(f"\n📋 업종별 비가맹점 현황 (상위 10개):")
            category_counts = non_members['업종명(종목명)'].value_counts().head(10)
            for i, (category, count) in enumerate(category_counts.items(), 1):
                print(f"   {i:2d}. {category}: {count}개")
        
        # 지역별 비가맹점 현황
        if '소재지지번주소' in non_members.columns:
            print(f"\n🗺️  지역별 비가맹점 분포:")
            # 주소에서 동 정보 추출
            non_members['동'] = non_members['소재지지번주소'].str.extract(r'용인시 수지구 (\w+동)')
            dong_counts = non_members['동'].value_counts().head(10)
            for i, (dong, count) in enumerate(dong_counts.items(), 1):
                if pd.notna(dong):
                    print(f"   {i:2d}. {dong}: {count}개")
        
        print(f"\n🎉 비가맹점 추출 완료!")
        print(f"📋 Excel 파일에서 '비가맹점' 시트를 확인하세요!")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result_file = extract_non_members()
    if result_file:
        print(f"\n🎊 작업 완료!")
        print(f"📁 결과 파일: {result_file}")
        print(f"📋 Excel에서 두 개 시트를 확인할 수 있습니다:")
        print(f"   - '전체결과': 모든 조회 결과")
        print(f"   - '비가맹점': 현대카드 사용 불가 업체만")