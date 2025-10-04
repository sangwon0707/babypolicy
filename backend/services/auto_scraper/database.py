"""
범용 PDF 자동 스크래퍼 ver1.2 - 데이터베이스 이력 관리

ver1.2 새로운 기능:
- 처리된 게시물 URL 추적 테이블 추가 (중복 방문 방지)
- 게시판 패턴 캐시 테이블 추가 (패턴 학습)
- 빠른 조회를 위한 인덱스 최적화
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from config import LOG_DIR, PROCESSED_ARTICLES_EXPIRE_DAYS

# DB 파일 경로
DB_FILE = os.path.join(LOG_DIR, 'download_history.db')


# ============================================
# 데이터베이스 초기화
# ============================================

def init_database():
    """
    데이터베이스 초기화 (테이블 생성)

    Returns:
        bool: 성공 여부
    """
    try:
        os.makedirs(LOG_DIR, exist_ok=True)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # 다운로드 이력 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_title TEXT NOT NULL,
                article_url TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_hash TEXT,
                file_size TEXT,
                download_method TEXT,
                timestamp TEXT NOT NULL,
                UNIQUE(article_url, filename)
            )
        ''')

        # 해시 인덱스 (빠른 중복 검사)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_hash
            ON downloads(file_hash)
        ''')

        # 파일명 인덱스
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_filename
            ON downloads(filename)
        ''')

        # 실패 이력 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_title TEXT NOT NULL,
                article_url TEXT NOT NULL,
                reason TEXT,
                timestamp TEXT NOT NULL
            )
        ''')

        # ver1.2: 처리된 게시물 추적 테이블 (중복 방문 방지)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_url TEXT NOT NULL UNIQUE,
                article_title TEXT,
                process_status TEXT NOT NULL,
                pdf_count INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL,
                last_accessed TEXT NOT NULL
            )
        ''')

        # 처리된 게시물 URL 인덱스
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_processed_url
            ON processed_articles(article_url)
        ''')

        # ver1.2: 게시판 패턴 캐시 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS board_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_domain TEXT NOT NULL,
                link_selector TEXT,
                pagination_selector TEXT,
                pdf_strategy TEXT,
                success_count INTEGER DEFAULT 0,
                total_attempts INTEGER DEFAULT 0,
                confidence REAL DEFAULT 0.0,
                last_used TEXT NOT NULL,
                UNIQUE(board_domain)
            )
        ''')

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        print(f"DB 초기화 오류: {e}")
        return False


# ============================================
# 다운로드 이력 관리
# ============================================

def add_download_record(article_title, article_url, filename, file_hash=None, file_size=None, method=None):
    """
    다운로드 기록 추가

    Args:
        article_title: 게시글 제목
        article_url: 게시글 URL
        filename: 파일명
        file_hash: SHA256 해시 (선택)
        file_size: 파일 크기 (선택)
        method: 다운로드 방식 (선택)

    Returns:
        bool: 성공 여부
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT OR REPLACE INTO downloads
            (article_title, article_url, filename, file_hash, file_size, download_method, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (article_title, article_url, filename, file_hash, file_size, method, timestamp))

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        print(f"다운로드 기록 추가 오류: {e}")
        return False


def is_duplicate_by_filename(filename):
    """
    파일명으로 중복 체크

    Args:
        filename: 파일명

    Returns:
        bool: 이미 다운로드된 경우 True
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM downloads WHERE filename = ?', (filename,))
        count = cursor.fetchone()[0]

        conn.close()

        return count > 0

    except Exception as e:
        print(f"파일명 중복 체크 오류: {e}")
        return False


def is_duplicate_by_hash(file_hash):
    """
    SHA256 해시로 중복 체크

    Args:
        file_hash: SHA256 해시

    Returns:
        dict or None: 중복된 파일 정보 또는 None
    """
    try:
        if not file_hash:
            return None

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT filename, article_title, timestamp
            FROM downloads
            WHERE file_hash = ?
        ''', (file_hash,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'filename': result[0],
                'article_title': result[1],
                'timestamp': result[2]
            }

        return None

    except Exception as e:
        print(f"해시 중복 체크 오류: {e}")
        return None


def is_duplicate_by_url_filename(article_url, filename):
    """
    URL + 파일명 조합으로 중복 체크

    Args:
        article_url: 게시글 URL
        filename: 파일명

    Returns:
        bool: 이미 다운로드된 경우 True
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM downloads
            WHERE article_url = ? AND filename = ?
        ''', (article_url, filename))

        count = cursor.fetchone()[0]
        conn.close()

        return count > 0

    except Exception as e:
        print(f"URL+파일명 중복 체크 오류: {e}")
        return False


# ============================================
# ver1.2: 처리된 게시물 추적 (중복 방문 방지)
# ============================================

def is_article_processed(article_url):
    """
    게시물이 이미 처리되었는지 확인

    Args:
        article_url: 게시글 URL

    Returns:
        dict or None: 처리 정보 또는 None
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT process_status, pdf_count, timestamp
            FROM processed_articles
            WHERE article_url = ?
        ''', (article_url,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'status': result[0],
                'pdf_count': result[1],
                'timestamp': result[2]
            }

        return None

    except Exception as e:
        print(f"게시물 처리 확인 오류: {e}")
        return None


def mark_article_processed(article_url, article_title, status, pdf_count=0):
    """
    게시물을 처리 완료로 표시

    Args:
        article_url: 게시글 URL
        article_title: 게시글 제목
        status: 처리 상태 ('success', 'no_pdf', 'error', 'skipped')
        pdf_count: 다운로드된 PDF 개수

    Returns:
        bool: 성공 여부
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT OR REPLACE INTO processed_articles
            (article_url, article_title, process_status, pdf_count, timestamp, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (article_url, article_title, status, pdf_count, timestamp, timestamp))

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        print(f"게시물 처리 표시 오류: {e}")
        return False


def update_article_access_time(article_url):
    """
    게시물 마지막 접근 시간 업데이트

    Args:
        article_url: 게시글 URL

    Returns:
        bool: 성공 여부
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            UPDATE processed_articles
            SET last_accessed = ?
            WHERE article_url = ?
        ''', (timestamp, article_url))

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        print(f"접근 시간 업데이트 오류: {e}")
        return False


def cleanup_old_processed_articles():
    """
    오래된 처리 기록 삭제

    Returns:
        int: 삭제된 레코드 수
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        expire_date = (datetime.now() - timedelta(days=PROCESSED_ARTICLES_EXPIRE_DAYS)).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            DELETE FROM processed_articles
            WHERE last_accessed < ?
        ''', (expire_date,))

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted_count

    except Exception as e:
        print(f"오래된 기록 삭제 오류: {e}")
        return 0


# ============================================
# ver1.2: 게시판 패턴 캐시
# ============================================

def get_board_pattern(board_domain):
    """
    게시판 도메인의 학습된 패턴 조회

    Args:
        board_domain: 게시판 도메인

    Returns:
        dict or None: 패턴 정보 또는 None
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT link_selector, pagination_selector, pdf_strategy, confidence
            FROM board_patterns
            WHERE board_domain = ?
        ''', (board_domain,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'link_selector': result[0],
                'pagination_selector': result[1],
                'pdf_strategy': result[2],
                'confidence': result[3]
            }

        return None

    except Exception as e:
        print(f"게시판 패턴 조회 오류: {e}")
        return None


def save_board_pattern(board_domain, link_selector=None, pagination_selector=None,
                       pdf_strategy=None, success=True):
    """
    게시판 패턴 저장 또는 업데이트

    Args:
        board_domain: 게시판 도메인
        link_selector: 링크 선택자
        pagination_selector: 페이지네이션 선택자
        pdf_strategy: PDF 다운로드 전략
        success: 성공 여부

    Returns:
        bool: 성공 여부
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 기존 레코드 조회
        cursor.execute('''
            SELECT success_count, total_attempts
            FROM board_patterns
            WHERE board_domain = ?
        ''', (board_domain,))

        result = cursor.fetchone()

        if result:
            # 업데이트
            success_count = result[0] + (1 if success else 0)
            total_attempts = result[1] + 1
            confidence = success_count / total_attempts if total_attempts > 0 else 0.0

            cursor.execute('''
                UPDATE board_patterns
                SET success_count = ?, total_attempts = ?, confidence = ?, last_used = ?
                WHERE board_domain = ?
            ''', (success_count, total_attempts, confidence, timestamp, board_domain))
        else:
            # 새로 삽입
            success_count = 1 if success else 0
            total_attempts = 1
            confidence = success_count / total_attempts if total_attempts > 0 else 0.0

            cursor.execute('''
                INSERT INTO board_patterns
                (board_domain, link_selector, pagination_selector, pdf_strategy,
                 success_count, total_attempts, confidence, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (board_domain, link_selector, pagination_selector, pdf_strategy,
                  success_count, total_attempts, confidence, timestamp))

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        print(f"게시판 패턴 저장 오류: {e}")
        return False


# ============================================
# 실패 이력 관리
# ============================================

def add_failure_record(article_title, article_url, reason):
    """
    실패 기록 추가

    Args:
        article_title: 게시글 제목
        article_url: 게시글 URL
        reason: 실패 사유

    Returns:
        bool: 성공 여부
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO failures (article_title, article_url, reason, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (article_title, article_url, reason, timestamp))

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        print(f"실패 기록 추가 오류: {e}")
        return False


# ============================================
# 통계 조회
# ============================================

def get_download_stats():
    """
    다운로드 통계 조회

    Returns:
        dict: 통계 정보
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # 전체 다운로드 수
        cursor.execute('SELECT COUNT(*) FROM downloads')
        total_downloads = cursor.fetchone()[0]

        # 전체 실패 수
        cursor.execute('SELECT COUNT(*) FROM failures')
        total_failures = cursor.fetchone()[0]

        # 처리된 게시물 수
        cursor.execute('SELECT COUNT(*) FROM processed_articles')
        total_processed = cursor.fetchone()[0]

        # 다운로드 방법별 통계
        cursor.execute('''
            SELECT download_method, COUNT(*)
            FROM downloads
            GROUP BY download_method
        ''')
        methods = cursor.fetchall()

        conn.close()

        return {
            'total_downloads': total_downloads,
            'total_failures': total_failures,
            'total_processed': total_processed,
            'methods': {method: count for method, count in methods if method}
        }

    except Exception as e:
        print(f"통계 조회 오류: {e}")
        return {
            'total_downloads': 0,
            'total_failures': 0,
            'total_processed': 0,
            'methods': {}
        }


def get_recent_downloads(limit=10):
    """
    최근 다운로드 기록 조회

    Args:
        limit: 조회할 개수

    Returns:
        list: 다운로드 기록 리스트
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT article_title, filename, file_size, timestamp
            FROM downloads
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))

        results = cursor.fetchall()
        conn.close()

        return [
            {
                'title': row[0],
                'filename': row[1],
                'size': row[2],
                'timestamp': row[3]
            }
            for row in results
        ]

    except Exception as e:
        print(f"최근 다운로드 조회 오류: {e}")
        return []


# ============================================
# JSON 로그 마이그레이션
# ============================================

def migrate_from_json(json_file_path):
    """
    기존 JSON 로그 파일을 DB로 마이그레이션

    Args:
        json_file_path: JSON 로그 파일 경로

    Returns:
        int: 마이그레이션된 레코드 수
    """
    if not os.path.exists(json_file_path):
        return 0

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        downloads = data.get('downloads', [])
        count = 0

        for record in downloads:
            success = add_download_record(
                article_title=record.get('title', 'N/A'),
                article_url=record.get('url', 'N/A'),
                filename=record.get('filename', 'unknown.pdf'),
                file_size=record.get('size'),
                method=record.get('method')
            )

            if success:
                count += 1

        print(f"✅ {count}개 레코드를 JSON에서 DB로 마이그레이션했습니다.")
        return count

    except Exception as e:
        print(f"JSON 마이그레이션 오류: {e}")
        return 0


# ============================================
# DB 초기화 자동 실행
# ============================================

# 모듈 import 시 자동으로 DB 초기화
init_database()
