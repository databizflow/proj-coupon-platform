import pandas as pd
import openpyxl
from openpyxl import load_workbook

def extract_convenience_stores():
    print("🏪 편의점 추출 시작!")
    print("=" * 50)
    
    try:
        # Excel 파일 읽기
        file_path = '현대카드_가맹점_최종분석결과_수작업중.xlsx'
        
        # 비가맹점 시트 읽기
        df_non_members = pd.read_excel(file_path, sheet_name='비가맹점')
        print(f"📊 비가맹점 데이터: {len(df_non_members)}개")
        
        # CU 편의점 필터링
        cu_filter = (
            df_non_members['상호명'].str.contains('CU|씨유', case=False, na=False) &
            df_non_members['업종명(종목명)'].str.contains('편의점', na=False)
        )
        cu_stores = df_non_members[cu_filter].copy()
        print(f"🏪 CU 편의점: {len(cu_stores)}개")
        
        # GS25 편의점 필터링
        gs25_filter = (
            df_non_members['상호명'].str.contains('GS25|지에스25|지에스|GS', case=False, na=False) &
            df_non_members['업종명(종목명)'].str.contains('편의점', na=False)
        )
        gs25_stores = df_non_members[gs25_filter].copy()
        print(f"🏪 GS25 편의점: {len(gs25_stores)}개")
        
        # 전체 편의점 (CU + GS25)
        all_convenience = pd.concat([cu_stores, gs25_stores], ignore_index=True)
        # 중복 제거 (혹시 있을 수 있는)
        all_convenience = all_convenience.drop_duplicates()
        print(f"🏪 전체 편의점: {len(all_convenience)}개")
        
        if len(cu_stores) == 0 and len(gs25_stores) == 0:
            print("⚠️  해당 조건의 편의점이 없습니다.")
            return
        
        # 기존 Excel 파일에 새 시트 추가
        output_file = '현대카드_가맹점_최종분석결과_편의점추가.xlsx'
        
        # 기존 파일의 모든 시트 복사
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 기존 시트들 복사
            try:
                # 전체결과 시트
                df_all = pd.read_excel(file_path, sheet_name='전체결과')
                df_all.to_excel(writer, sheet_name='전체결과', index=False)
                print(f"✅ '전체결과' 시트 복사: {len(df_all)}개")
            except:
                print("⚠️  '전체결과' 시트 없음")
            
            try:
                # 비가맹점 시트
                df_non_members.to_excel(writer, sheet_name='비가맹점', index=False)
                print(f"✅ '비가맹점' 시트 복사: {len(df_non_members)}개")
            except:
                print("⚠️  '비가맹점' 시트 없음")
            
            try:
                # 가맹점 시트
                df_members = pd.read_excel(file_path, sheet_name='가맹점')
                df_members.to_excel(writer, sheet_name='가맹점', index=False)
                print(f"✅ '가맹점' 시트 복사: {len(df_members)}개")
            except:
                print("⚠️  '가맹점' 시트 없음")
            
            # 새 시트들 추가
            if len(cu_stores) > 0:
                cu_stores.to_excel(writer, sheet_name='CU편의점', index=False)
                print(f"🆕 'CU편의점' 시트 생성: {len(cu_stores)}개")
            
            if len(gs25_stores) > 0:
                gs25_stores.to_excel(writer, sheet_name='GS25편의점', index=False)
                print(f"🆕 'GS25편의점' 시트 생성: {len(gs25_stores)}개")
            
            if len(all_convenience) > 0:
                all_convenience.to_excel(writer, sheet_name='전체편의점', index=False)
                print(f"🆕 '전체편의점' 시트 생성: {len(all_convenience)}개")
        
        print(f"\n💾 Excel 파일 저장 완료!")
        print(f"📁 파일명: {output_file}")
        
        # 상세 분석
        print(f"\n📊 편의점 상세 분석:")
        
        if len(cu_stores) > 0:
            print(f"\n🏪 CU 편의점 목록:")
            for i, (idx, row) in enumerate(cu_stores.iterrows(), 1):
                store_name = row['상호명']
                address = row.get('소재지지번주소', 'N/A')
                # 주소에서 동 정보 추출
                if '용인시 수지구' in str(address):
                    dong = str(address).split('용인시 수지구')[1].split()[0] if '용인시 수지구' in str(address) else 'N/A'
                else:
                    dong = 'N/A'
                print(f"   {i:2d}. {store_name} ({dong})")
        
        if len(gs25_stores) > 0:
            print(f"\n🏪 GS25 편의점 목록:")
            for i, (idx, row) in enumerate(gs25_stores.iterrows(), 1):
                store_name = row['상호명']
                address = row.get('소재지지번주소', 'N/A')
                # 주소에서 동 정보 추출
                if '용인시 수지구' in str(address):
                    dong = str(address).split('용인시 수지구')[1].split()[0] if '용인시 수지구' in str(address) else 'N/A'
                else:
                    dong = 'N/A'
                print(f"   {i:2d}. {store_name} ({dong})")
        
        # 지역별 분포
        if len(all_convenience) > 0:
            print(f"\n🗺️  편의점 지역별 분포:")
            all_convenience['동'] = all_convenience['소재지지번주소'].str.extract(r'용인시 수지구 (\w+동)')
            dong_counts = all_convenience['동'].value_counts()
            for i, (dong, count) in enumerate(dong_counts.items(), 1):
                if pd.notna(dong):
                    print(f"   {i:2d}. {dong}: {count}개")
        
        print(f"\n🎉 편의점 추출 완료!")
        print(f"📋 Excel 파일에서 새로 추가된 시트들을 확인하세요!")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result_file = extract_convenience_stores()
    if result_file:
        print(f"\n🎊 작업 완료!")
        print(f"📁 결과 파일: {result_file}")
        print(f"📋 새로 추가된 시트들:")
        print(f"   - 'CU편의점': CU 브랜드 편의점만")
        print(f"   - 'GS25편의점': GS25 브랜드 편의점만") 
        print(f"   - '전체편의점': CU + GS25 통합")