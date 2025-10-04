"""
범용 PDF 자동 스크래퍼 ver1.4.1 - 설정 파일

ver1.4.1 핵심 개선사항:
🔒 개인정보 보호 (정보통신망법 준수):
  - 이메일 주소 수집 금지
  - 전화번호, 주민번호 등 개인정보 필터링
  - PDF 파일만 다운로드 (다른 파일 형식 차단)
  - 로그에 개인정보 자동 제거

ver1.4 핵심 개선사항:
🎯 안정성 및 성능 최적화:
  - 타임아웃 최적화 (page_load: 30→20, element_wait: 20→10, download_wait: 60→30, page_stable: 15→5)
  - 빠른 모드 지원으로 속도 향상
  - 페이지 단위 학습 로직

ver1.3 기능 유지:
- 전략 패턴 학습 시스템
- 게시판별 전략 성공률 자동 학습
- 이미지 차단으로 메모리 절약 (40-60%)
- 해시 기반 중복 체크
"""

import os

# --- 경로 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 프로젝트 루트 경로 찾기 (backend/services/auto_scraper -> 루트)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..', '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DOWNLOAD_DIR = os.path.join(DATA_DIR, 'pdfs', 'auto_scraper')
LOG_DIR = os.path.join(DATA_DIR, 'logs')

# 로그 파일들
DOWNLOAD_LOG_FILE = os.path.join(LOG_DIR, 'download_log.json')
FAILED_LOG_FILE = os.path.join(LOG_DIR, 'failed_log.json')
CHECKPOINT_FILE = os.path.join(LOG_DIR, 'checkpoint.json')
DEBUG_LOG_FILE = os.path.join(LOG_DIR, 'debug_log.txt')

# ver1.2: 기존 캐시 파일들 (비활성화)
BOARD_PATTERN_CACHE = os.path.join(LOG_DIR, 'board_patterns.json')  # 사용 안 함
PROCESSED_ARTICLES_DB = os.path.join(LOG_DIR, 'processed_articles.db')  # 사용 안 함

# ver1.3: 전략 학습 파일 (NEW!)
LEARNED_STRATEGIES_FILE = os.path.join(LOG_DIR, 'learned_strategies.json')  # 전략 학습 데이터

# --- 디버그 레벨 ---
DEBUG_LEVELS = {
    'ERROR': 0,
    'WARNING': 1,
    'INFO': 2,
    'DEBUG': 3,
    'VERBOSE': 4
}

CURRENT_DEBUG_LEVEL = DEBUG_LEVELS['VERBOSE']  # LH 디버깅용 (VERBOSE 레벨)

# --- PDF 탐지 키워드 (다국어) ---
DOWNLOAD_KEYWORDS = {
    'korean': ['다운로드', '내려받기', '저장', 'pdf', '파일받기', '받기'],
    'english': ['download', 'get', 'save', 'pdf', 'file'],
    'chinese': ['下载', '下載'],
    'japanese': ['ダウンロード']
}

ATTACHMENT_KEYWORDS = {
    'korean': ['첨부파일', '첨부', '파일', '자료'],
    'english': ['attachment', 'file', 'document'],
    'chinese': ['附件'],
    'japanese': ['添付ファイル', '添付']
}

PREVIEW_KEYWORDS = {
    'korean': ['미리보기', '미리 보기', '보기', '열기'],
    'english': ['preview', 'view', 'open'],
    'chinese': ['预览', '預覽'],
    'japanese': ['プレビュー']
}

# --- 게시판 링크 탐지 키워드 ---
BOARD_LINK_PATTERNS = [
    'view', 'detail', 'read', 'show', 'article',
    'no=', 'id=', 'num=', 'seq=', 'idx=',
    'board', 'post', 'notice', 'bbs'
]

# --- 페이지네이션 키워드 ---
NEXT_PAGE_KEYWORDS = {
    'korean': ['다음', '다음페이지', '다음 페이지'],
    'english': ['next', 'next page'],
    'chinese': ['下一页', '下一頁'],
    'japanese': ['次へ', '次のページ']
}

# --- 타임아웃 설정 (초) - ver1.4 최적화 ---
TIMEOUT = {
    'page_load': 20,           # 페이지 로딩 대기 (30 → 20, 불필요하게 김)
    'element_wait': 10,        # 요소 대기 (20 → 10)
    'download_wait': 30,       # 다운로드 대기 (60 → 30)
    'page_stable': 5           # 페이지 안정화 대기 (15 → 5, 너무 보수적)
}

# --- 재시도 설정 ---
MAX_RETRIES = 2                # 최대 재시도 횟수 (3 → 2)
RETRY_DELAY = 1                # 재시도 간격 (2 → 1초)

# --- 브라우저 설정 ---
BROWSER_RESTART_INTERVAL = 50  # N개 게시글마다 브라우저 재시작 (30 → 50)

# --- PDF 검증 설정 ---
MIN_PDF_SIZE = 100             # 최소 PDF 파일 크기 (바이트)
PDF_HEADER = b'%PDF'           # PDF 파일 헤더 시그니처

# --- 안전 모드 설정 ---
SAFE_MODE = True               # 위험한 링크 클릭 방지

# 안전 블랙리스트 패턴
DANGEROUS_PATTERNS = [
    'certificate', '인증서', '공동인증서',
    'login', '로그인', 'auth', 'sign',
    'logout', '로그아웃',
    'delete', '삭제', 'remove',
    'modify', '수정', 'edit'
]

# --- 게시글 링크 필터 설정 ---
MIN_LINK_TEXT_LENGTH = 3       # 최소 링크 텍스트 길이
MAX_LINK_TEXT_LENGTH = 200     # 최대 링크 텍스트 길이

# 제외할 링크 텍스트 패턴
EXCLUDE_LINK_TEXTS = [
    '더보기', '상세보기', 'more', 'detail',
    '이전', '다음', 'prev', 'next',
    '목록', 'list', '처음', 'first', '마지막', 'last',
    '수정', '삭제', 'edit', 'delete',
    '답글', '댓글', 'reply', 'comment'
]

# --- 출력 설정 ---
SHOW_PROGRESS_BAR = True       # 진행률 표시
SHOW_DETAILED_LOG = True       # 상세 로그 표시
SHOW_SUCCESS_EMOJI = True      # 이모지 사용

# --- 기타 설정 ---
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


# ============================================
# ver1.2 최적화 설정
# ============================================

# --- 성능 최적화 ---
HEADLESS_MODE = False           # Headless 모드 (GUI 없이 실행)
BLOCK_IMAGES = True             # 이미지 로딩 차단 (False → True로 메모리 절약)
BLOCK_ADS = True                # 광고 차단

# 차단할 리소스 타입
BLOCKED_RESOURCE_TYPES = ['image', 'stylesheet', 'font', 'media']
BLOCKED_DOMAINS = [
    'doubleclick.net', 'googlesyndication.com', 'adservice.google.com',
    'googleadservices.com', 'google-analytics.com'
]

# --- 다중 PDF 다운로드 ---
DOWNLOAD_ALL_PDFS = True        # 게시물당 모든 PDF 다운로드
MAX_PDFS_PER_ARTICLE = 10       # 게시물당 최대 PDF 개수

# --- 중복 체크 방식 ---
USE_FILENAME_CHECK = True       # 파일명 기반 중복 체크
USE_HASH_CHECK = True           # SHA256 해시 기반 중복 체크
USE_DATABASE = True             # SQLite DB 이력 관리

# --- ver1.2: 게시물 URL 추적 (중복 방문 방지) ---
TRACK_PROCESSED_ARTICLES = False        # 처리된 게시물 URL 추적 (비활성화: DB 부하)
SKIP_PROCESSED_ARTICLES = False         # 이미 처리된 게시물 건너뛰기 (비활성화)
PROCESSED_ARTICLES_EXPIRE_DAYS = 90    # 처리 기록 유효 기간 (일)

# --- ver1.2: 게시판 패턴 학습 및 캐싱 ---
USE_BOARD_PATTERN_CACHE = False         # 게시판 유형 패턴 캐싱 (비활성화: 실효성 낮음)
LEARN_BOARD_PATTERNS = False            # 성공한 패턴 자동 학습 (비활성화)
PATTERN_CONFIDENCE_THRESHOLD = 0.7      # 패턴 신뢰도 임계값
MAX_PATTERN_CACHE_SIZE = 50             # 최대 캐시 크기

# --- ver1.2: 링크 추출 최적화 ---
CACHE_BOARD_LINKS = False               # 페이지당 링크 목록 캐싱 (비활성화: 불안정)
USE_SMART_LINK_EXTRACTION = False       # 첫 추출 시 패턴 학습, 이후 빠른 추출 (비활성화)

# --- 파일명 추출 전략 우선순위 ---
FILENAME_EXTRACT_PRIORITY = [
    'content_disposition',      # HTTP 헤더 우선
    'url',                      # URL 경로
    'text',                     # 링크 텍스트
    'onclick',                  # JavaScript
    'fallback'                  # 제목 + 타임스탬프
]

# --- ver1.3: 전략 학습 시스템 (NEW!) ---
USE_STRATEGY_LEARNING = True    # 전략 패턴 학습 활성화 (핵심 기능!)
STRATEGY_SCORE_THRESHOLD = 0.2  # 이 점수 미만 전략은 스킵
CONSECUTIVE_FAIL_THRESHOLD = 5  # 연속 N회 실패 시 전략 스킵

# --- 자동 학습 기능 (ver1.2, 유지) ---
AUTO_LEARN_STRATEGY = True      # 성공률 높은 전략 우선순위 자동 조정
STRATEGY_LEARN_FILE = os.path.join(LOG_DIR, 'strategy_stats.json')  # 구버전 파일 (ver1.3은 learned_strategies.json 사용)

# --- ver1.4.1: 개인정보 보호 설정 (정보통신망법 준수) ---
ENABLE_PRIVACY_PROTECTION = True         # 개인정보 보호 활성화
BLOCK_EMAIL_COLLECTION = True            # 이메일 주소 수집 차단
BLOCK_PHONE_COLLECTION = True            # 전화번호 수집 차단
SANITIZE_LOGS = True                     # 로그에서 개인정보 자동 제거
PDF_ONLY_MODE = True                     # PDF 파일만 다운로드 (다른 형식 차단)

# 허용된 파일 확장자 (PDF만)
ALLOWED_FILE_EXTENSIONS = ['.pdf']

# 차단할 파일 확장자 (개인정보 포함 가능성)
BLOCKED_FILE_EXTENSIONS = [
    '.txt', '.csv', '.xlsx', '.xls',    # 데이터 파일
    '.doc', '.docx', '.hwp',            # 문서 파일
    '.zip', '.rar', '.7z',              # 압축 파일
    '.exe', '.bat', '.sh',              # 실행 파일
    '.html', '.htm', '.xml', '.json'    # 웹/데이터 파일
]

# ver1.4.2: 동적 스크립트 확장자 (PDF가 아니지만 다운로드 처리에 사용)
# SH/LH 등 공공기관 사이트 대응
DYNAMIC_SCRIPT_EXTENSIONS = [
    '.php',   # SH 사이트 (i-sh.co.kr)
    '.do',    # LH 사이트 (apply.lh.or.kr), Spring Framework
    '.asp',   # ASP 기반 사이트
    '.aspx',  # ASP.NET 사이트
    '.jsp',   # Java 기반 사이트
    '.ashx',  # HTTP Handler
    '.py',    # Python 스크립트
    '.cgi',   # CGI 스크립트
]

# --- 고급 설정 ---
REMOVE_DUPLICATE_AFTER_DOWNLOAD = True   # 다운로드 후 해시 중복 시 자동 삭제
NORMALIZE_FILENAMES = True               # 파일명 자동 정규화
VERIFY_PDF_INTEGRITY = True              # PDF 무결성 검증 강화

# --- 미리보기 및 새 창 처리 ---
SKIP_PREVIEW_BUTTONS = True              # 미리보기 버튼 건너뛰기
CLOSE_NEW_WINDOWS = True                 # 클릭 시 새 창 열리면 자동 닫기
PREFER_FILENAME_LINKS = True             # 파일명 직접 링크 우선 사용

# 미리보기 키워드 (이 키워드 포함 시 낮은 우선순위)
PREVIEW_KEYWORDS_FILTER = ['미리보기', '미리 보기', 'preview', 'view', '보기']

# --- ver1.2: 페이지 안정화 최적화 ---
QUICK_PAGE_STABLE_CHECK = False          # 빠른 페이지 안정화 체크 (비활성화: 안정성 우선)
REDUCE_WAIT_TIMES = False                # 대기 시간 자동 단축 (비활성화)
