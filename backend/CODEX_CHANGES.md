# 2025-10-08 변경 내역

- `services/babypolicy_chat/ingest.py` (약 38-95행):
  - `_resolve_ingest_path` 헬퍼를 추가해 절대 경로와 작업공간 기준 상대 경로 모두를 해석하도록 했습니다. 프로젝트 루트와 형제 `data/` 디렉터리를 우선 탐색하므로 `pdfs/booklet.pdf`처럼 저장된 값도 실제 파일 경로로 자동 변환됩니다.
  - 임베딩 전에 경로 존재 여부와 디렉터리 여부를 확인해, 파일이 없으면 `missing`, 디렉터리를 가리키면 `skipped` 상태로 기록하도록 방어 로직을 넣었습니다. 잘못된 경로가 저장돼도 명확한 상태 메시지를 받을 수 있습니다.
- `services/babypolicy_chat/ingest.py` (약 97-156행):
  - Supabase `pdf_files` 테이블 대신 프로젝트 루트의 `data/` 폴더를 재귀적으로 스캔해 PDF를 찾도록 변경했습니다. 파일이 하나도 없으면 `error` 상태와 함께 “data 폴더에 PDF 파일이 없습니다.” 메시지를 반환해 임베딩 실패를 알립니다.
  - 각 PDF는 상대 경로를 기반으로 `data-...` 형태의 고유 `policy_id`를 생성하고, 동일한 헬퍼로 만들어진 메타데이터와 함께 `BabyPolicyChatService.ingest_pdf`에 전달되어 벡터 DB에 저장됩니다.
  - `data/` 폴더가 항상 `babypolicy/` 바로 아래에 있다고 가정하고 그 경로만 사용하도록 고정했습니다.
