import pandas as pd
import re

def separate_cu_store_names():
    print("🏪 CU편의점 상호명 분리 시작!")
    print("=" * 50)
    
    try:
        # Excel 파일 읽기
        file_path = '현대카드_가맹점_최종분석결과_편의점추가.xlsx'
        
        # CU편의점 시트 읽기
        df_cu = pd.read_excel(file_path, sheet_name='CU편의점')
        print(f"📊 CU편의점 데이터: {len(df_cu)}개")
        
        # 상호명 분리 함수
        def separate_store_name(store_name):
            if pd.isna(store_name):
                return '', store_name
            
            store_name = str(store_name)
            
            # 다양한 패턴으로 브랜드명과 지점명 분리
            patterns = [
                r'^(씨유\(CU\))\s*(.+)$',
                r'^(씨유)\s*(.+)$', 
                r'^(CU)\s*(.+)$',
                r'^(비지에프리테일\(씨유[^)]*\))\s*(.*)$',
                r'^(지에스리테일\([^)]*\))\s*(.*)$'
            ]
            
            for pattern in patterns:
                match = re.match(pattern, store_name, re.IGNORECASE)
                if match:
                    brand = match.group(1).strip()
                    location = match.group(2).strip()
                    return brand, location
            
            # 패턴에 맞지 않으면 전체를 지점명으로
            return '', store_name
        
        # 상호명 분리 적용
        print("\n🔄 상호명 분리 중...")
        df_cu[['브랜드명', '지점명']] = df_cu['상호명'].apply(
            lambda x: pd.Series(separate_store_name(x))
        )
        
        # 결과 확인
        print(f"✅ 분리 완료!")
        
        # 브랜드명별 통계
        brand_counts = df_cu['브랜드명'].value_counts()
        print(f"\n📊 브랜드명별 분포:")
        for brand, count in brand_counts.items():
            if brand:  # 빈 문자열이 아닌 경우만
                print(f"   - {brand}: {count}개")
        
        # 빈 브랜드명 (패턴에 맞지 않는 것들)
        empty_brand = df_cu[df_cu['브랜드명'] == '']
        if len(empty_brand) > 0:
            print(f"   - 기타 (패턴 미매치): {len(empty_brand)}개")
            print(f"     예시: {empty_brand['상호명'].iloc[0] if len(empty_brand) > 0 else 'N/A'}")
        
        # 컬럼 순서 재정렬 (브랜드명, 지점명을 상호명 다음에 배치)
        columns = df_cu.columns.tolist()
        
        # 상호명 인덱스 찾기
        store_name_idx = columns.index('상호명')
        
        # 새로운 컬럼 순서 생성
        new_columns = (
            columns[:store_name_idx + 1] +  # 상호명까지
            ['브랜드명', '지점명'] +  # 새 컬럼들
            [col for col in columns[store_name_idx + 1:] if col not in ['브랜드명', '지점명']]  # 나머지
        )
        
        df_cu = df_cu[new_columns]
        
        # 기존 Excel 파일의 모든 시트를 유지하면서 CU편의점 시트만 업데이트
        output_file = '현대카드_가맹점_최종분석결과_편의점분리완료.xlsx'
        
        # 기존 파일의 모든 시트 읽기
        excel_data = {}
        try:
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names:
                if sheet_name == 'CU편의점':
                    excel_data[sheet_name] = df_cu  # 수정된 데이터 사용
                else:
                    excel_data[sheet_name] = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"📋 시트 로드: {sheet_name}")
        except Exception as e:
            print(f"⚠️  기존 파일 읽기 오류: {e}")
            excel_data = {'CU편의점': df_cu}
        
        # Excel 파일로 저장
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet_name, data in excel_data.items():
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"💾 시트 저장: {sheet_name} ({len(data)}개)")
        
        print(f"\n💾 Excel 파일 저장 완료!")
        print(f"📁 파일명: {output_file}")
        
        # 분리 결과 샘플 출력
        print(f"\n📋 분리 결과 샘플 (처음 10개):")
        print("=" * 80)
        for i, (idx, row) in enumerate(df_cu.head(10).iterrows()):
            print(f"{i+1:2d}. 원본: {row['상호명']}")
            print(f"    브랜드: '{row['브랜드명']}' | 지점: '{row['지점명']}'")
            print("-" * 60)
        
        print(f"\n🎉 CU편의점 상호명 분리 완료!")
        print(f"📊 총 {len(df_cu)}개 편의점의 상호명이 분리되었습니다!")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result_file = separate_cu_store_names()
    if result_file:
        print(f"\n🎊 작업 완료!")
        print(f"📁 결과 파일: {result_file}")
        print(f"📋 CU편의점 시트에 새로 추가된 컬럼:")
        print(f"   - '브랜드명': 씨유(CU), 씨유, CU 등")
        print(f"   - '지점명': 나머지 지점명 부분")