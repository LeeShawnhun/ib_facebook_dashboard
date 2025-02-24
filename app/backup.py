import os
from datetime import datetime
import shutil
from fastapi import UploadFile
import tempfile

def backup_database():
    try:
        # 현재 시간으로 백업 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'./backups/db_backup_{timestamp}.db'
        
        # backups 디렉토리가 없으면 생성
        os.makedirs('./backups', exist_ok=True)
        
        # 데이터베이스 파일 복사
        shutil.copy2('./sql_app.db', backup_path)
        
        return True, f"Database backed up to {backup_path}"
    except Exception as e:
        return False, str(e)

def restore_latest_backup():
    try:
        # backups 디렉토리에서 가장 최근 백업 파일 찾기
        backup_files = [f for f in os.listdir('./backups') if f.startswith('db_backup_')]
        if not backup_files:
            return False, "No backup files found"
            
        latest_backup = max(backup_files)
        backup_path = os.path.join('./backups', latest_backup)
        
        # 현재 DB 파일 교체
        shutil.copy2(backup_path, './sql_app.db')
        
        return True, f"Database restored from {backup_path}"
    except Exception as e:
        return False, str(e)

async def restore_from_upload(file: UploadFile):
    try:
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # 업로드된 파일 내용을 임시 파일에 복사
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # 현재 DB 파일 백업
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'./backups/db_backup_before_restore_{timestamp}.db'
            os.makedirs('./backups', exist_ok=True)
            shutil.copy2('./sql_app.db', backup_path)

            # 업로드된 파일을 DB 파일로 복사
            shutil.copy2(temp_path, './sql_app.db')
            
            # 임시 파일 삭제
            os.unlink(temp_path)
            
            return True, "Database restored successfully from uploaded file"
        except Exception as e:
            # 에러 발생 시 임시 파일 삭제
            os.unlink(temp_path)
            raise e
            
    except Exception as e:
        return False, f"Failed to restore database: {str(e)}"