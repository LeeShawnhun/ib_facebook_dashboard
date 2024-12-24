import sqlite3
import os
from datetime import datetime
import shutil

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