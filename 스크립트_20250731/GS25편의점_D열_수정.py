import pandas as pd
import re

def modify_gs25_d_column():
    print("🏪 GS25편의점 D열 수정 시작!")
    print("=" * 50)
    
    try:
        # Excel 파일 읽기
        file_path = '편의점시트추출수정중.xlsx'
        
        # 먼저 파일의 시트 목록 확인
        excel_file = pd.ExcelFile(file_path)
        print(f"📋 파일의 시트 목록: {excel_file.sheet_names}")
        
        # GS25 관련 시트 찾기
        gs25_sheet_name = None
        for sheet_name in excel_file.sheet_names:
            if 'GS25' in sheet_name or 'gs25' in sheet_name.lower():
                gs25_sheet_name = sheet_name
                break
        
        if gs25_sheet_name is None:
            print("❌ GS25 관련 시트를 찾을 수 없습니다.")
            return None
        
        print(f"📍 찾은 GS25 시트: {gs25_sheet_name}")
        
        # GS25 시트 읽기
        df_gs25 = pd.read_excel(file_path, sheet_name=gs25_sheet_name)
        print(f"📊 GS25편의점 데이터: {len(df_gs25)}개")
        
        # 컬럼 확인
        print(f"📋 현재 컬럼: {list(df_gs25.columns)}")
        
        # D열 확인 (0-based index 3)
        if len(df_gs25.columns) >= 4:
            d_column = df_gs25.columns[3]  # D열
            print(f"📍 D열: {d_column}")
            
            # D열 수정 전 샘플 출력
            print(f"\n📋 수정 전 D열 샘플 (처음 10개):")
            print("=" * 60)
            for i, value in enumerate(df_gs25[d_column].head(10)):
                print(f"{i+1:2d}. {value}")
            
            # D열에서 "지에스25" 관련 텍스트 제거 함수
            def remove_gs25_prefix(text):
                if pd.isna(text):
                    return text
                
                text = str(text).strip()
                
                # 다양한 GS25 패턴 제거
                patterns = [
                    r'^지에스25\s*',           # 지에스25 
                    r'^지에스\(GS\)25\s*',     # 지에스(GS)25
                    r'^지에스\(GS\)25S\s*',    # 지에스(GS)25S
                    r'^GS25\s*',              # GS25
                    r'^GS리테일\([^)]*\)\s*',  # GS리테일(...)
                    r'^지에스리테일\([^)]*\)\s*' # 지에스리테일(...)
                ]
                
                for pattern in patterns:
                    text = re.sub(pattern, '', text, flags=re.IGNORECASE)
                
                return text.strip()
            
            # D열 수정 적용
            print(f"\n🔄 D열 수정 중...")
            df_gs25[d_column] = df_gs25[d_column].apply(remove_gs25_prefix)
            
            print(f"✅ D열 수정 완료!")
            
            # 수정 후 샘플 출력
            print(f"\n📋 수정 후 D열 샘플 (처음 10개):")
            print("=" * 60)
            for i, value in enumerate(df_gs25[d_column].head(10)):
                print(f"{i+1:2d}. {value}")
            
        else:
            print("❌ D열이 존재하지 않습니다.")
            return None
        
        # 기존 Excel 파일의 모든 시트를 유지하면서 GS25 시트만 업데이트
        output_file = '편의점시트추출수정완료.xlsx'
        
        # 기존 파일의 모든 시트 읽기
        excel_data = {}
        try:
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names:
                if sheet_name == 'GS25':
                    excel_data[sheet_name] = df_gs25  # 수정된 데이터 사용
                else:
                    excel_data[sheet_name] = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"📋 시트 로드: {sheet_name}")
        except Exception as e:
            print(f"⚠️  기존 파일 읽기 오류: {e}")
            excel_data = {'GS25': df_gs25}
        
        # Excel 파일로 저장
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet_name, data in excel_data.items():
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"💾 시트 저장: {sheet_name} ({len(data)}개)")
        
        print(f"\n💾 Excel 파일 저장 완료!")
        print(f"📁 파일명: {output_file}")
        
        # 수정 통계
        original_values = pd.read_excel(file_path, sheet_name=gs25_sheet_name)[d_column]
        modified_count = sum(1 for orig, mod in zip(original_values, df_gs25[d_column]) if str(orig) != str(mod))
        
        print(f"\n📊 수정 통계:")
        print(f"   - 총 데이터: {len(df_gs25)}개")
        print(f"   - 수정된 항목: {modified_count}개")
        print(f"   - 수정률: {modified_count/len(df_gs25)*100:.1f}%")
        
        print(f"\n🎉 GS25편의점 D열 수정 완료!")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result_file = modify_gs25_d_column()
    if result_file:
        print(f"\n🎊 작업 완료!")
        print(f"📁 결과 파일: {result_file}")
        print(f"📋 GS25 시트의 D열에서 '지에스25' 관련 텍스트가 제거되었습니다!")