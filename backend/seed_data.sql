-- BabyPolicy Dummy Data for Testing
-- Run this in Supabase SQL Editor after running init_supabase.sql

-- ========================
-- 1. Insert Test Users
-- ========================

-- Insert test users (password will be 'password123' hashed)
INSERT INTO users (id, email, password, provider, created_at) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'test1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYVPWzO6jK6', NULL, NOW()),
('550e8400-e29b-41d4-a716-446655440002', 'test2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYVPWzO6jK6', NULL, NOW()),
('550e8400-e29b-41d4-a716-446655440003', 'mommy@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYVPWzO6jK6', NULL, NOW()),
('550e8400-e29b-41d4-a716-446655440004', 'daddy@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYVPWzO6jK6', NULL, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert user profiles
INSERT INTO user_profiles (user_id, name, gender, region, income, family_size, updated_at) VALUES
('550e8400-e29b-41d4-a716-446655440001', '김민지', 'female', '서울특별시 강남구', 500, 3, NOW()),
('550e8400-e29b-41d4-a716-446655440002', '이준호', 'male', '경기도 수원시', 400, 4, NOW()),
('550e8400-e29b-41d4-a716-446655440003', '박수현', 'female', '부산광역시 해운대구', 350, 2, NOW()),
('550e8400-e29b-41d4-a716-446655440004', '정태현', 'male', '서울특별시 마포구', 600, 3, NOW())
ON CONFLICT (user_id) DO NOTHING;

-- Insert user settings
INSERT INTO user_settings (user_id, notify_policy, notify_event, language, theme) VALUES
('550e8400-e29b-41d4-a716-446655440001', true, true, 'ko', 'light'),
('550e8400-e29b-41d4-a716-446655440002', true, false, 'ko', 'light'),
('550e8400-e29b-41d4-a716-446655440003', false, true, 'ko', 'light'),
('550e8400-e29b-41d4-a716-446655440004', true, true, 'ko', 'light')
ON CONFLICT (user_id) DO NOTHING;

-- ========================
-- 2. Insert Sample Policies
-- ========================

INSERT INTO policies (id, title, description, category, region, eligibility, created_at) VALUES
('policy_001', '첫만남 이용권', '출생아 1인당 200만원 바우처 지급. 유흥, 사행성 업소 외 자유롭게 사용 가능', '출산지원', '전국', '{"age": "0세", "income": "제한없음"}', NOW()),
('policy_002', '부모급여', '0세 월 100만원, 1세 월 50만원 지급. 영아수당과 중복 불가', '양육지원', '전국', '{"age": "0-1세", "income": "제한없음"}', NOW()),
('policy_003', '아동수당', '8세 미만 아동에게 월 10만원 지급', '양육지원', '전국', '{"age": "0-7세", "income": "제한없음"}', NOW()),
('policy_004', '서울시 출산지원금', '첫째 20만원, 둘째 30만원, 셋째 이상 50만원', '출산지원', '서울특별시', '{"age": "출생시", "income": "제한없음"}', NOW()),
('policy_005', '경기도 청년 출산지원금', '첫째 100만원, 둘째 200만원, 셋째 이상 300만원', '출산지원', '경기도', '{"age": "출생시", "income": "청년부부"}', NOW())
ON CONFLICT (id) DO NOTHING;

-- ========================
-- 3. Insert Community Posts
-- ========================

INSERT INTO posts (id, title, content, author_id, category_id, likes_count, comments_count, views_count, status, created_at, updated_at, published_at) VALUES
(
  '650e8400-e29b-41d4-a716-446655440001',
  '첫만남 이용권 사용처 추천해주세요!',
  '출산 후 첫만남 이용권 200만원을 받았는데요, 어디에 쓰면 좋을까요? 다들 어디 사용하셨는지 궁금합니다. 분유, 기저귀는 필수로 사야할 것 같고... 유모차나 카시트도 고민 중이에요.',
  '550e8400-e29b-41d4-a716-446655440001',
  'tips',
  15,
  8,
  120,
  'published',
  NOW() - INTERVAL '2 days',
  NOW() - INTERVAL '2 days',
  NOW() - INTERVAL '2 days'
),
(
  '650e8400-e29b-41d4-a716-446655440002',
  '부모급여 신청 방법 공유합니다',
  '부모급여 신청하는 방법 정리해봤어요!

1. 복지로 홈페이지 접속
2. 부모급여 신청 클릭
3. 필요 서류 업로드
4. 2-3주 후 지급

저는 신청 후 정확히 18일 만에 받았습니다. 혹시 궁금하신 분들 계실까봐 공유드려요!',
  '550e8400-e29b-41d4-a716-446655440002',
  'policy',
  23,
  12,
  250,
  'published',
  NOW() - INTERVAL '1 day',
  NOW() - INTERVAL '1 day',
  NOW() - INTERVAL '1 day'
),
(
  '650e8400-e29b-41d4-a716-446655440003',
  '신생아 수면교육 팁',
  '아기 수면교육 시작한지 2주차인데 드디어 성공했어요! 처음엔 30분마다 깨서 너무 힘들었는데, 이제는 4시간씩 자요.

제가 한 방법:
- 낮잠 시간 일정하게 유지
- 밤에는 조명 최대한 어둡게
- 수유 후 트림 꼭 시키기
- 백색소음 활용

같은 고민 하시는 분들께 도움이 되길 바라요!',
  '550e8400-e29b-41d4-a716-446655440003',
  'tips',
  45,
  20,
  380,
  'published',
  NOW() - INTERVAL '3 hours',
  NOW() - INTERVAL '3 hours',
  NOW() - INTERVAL '3 hours'
),
(
  '650e8400-e29b-41d4-a716-446655440004',
  '육아휴직 신청했어요!',
  '드디어 육아휴직 신청했습니다. 회사에서 눈치가 좀 있긴 했지만, 아이와 함께할 시간이 더 소중하다고 생각해서 결정했어요.

육아휴직급여는 통상임금의 80%까지 받을 수 있고, 상한액은 월 150만원이에요. 신청은 생각보다 간단했습니다!',
  '550e8400-e29b-41d4-a716-446655440004',
  'support',
  18,
  5,
  95,
  'published',
  NOW() - INTERVAL '5 hours',
  NOW() - INTERVAL '5 hours',
  NOW() - INTERVAL '5 hours'
),
(
  '650e8400-e29b-41d4-a716-446655440005',
  '돌잔치 준비 체크리스트',
  '다음달이 우리 아기 돌이에요! 돌잔치 준비하면서 체크리스트 만들어봤습니다.

📝 준비사항:
- 돌잔치 장소 예약 (3개월 전)
- 돌복 주문 (2개월 전)
- 답례품 준비 (1개월 전)
- 돌상 세팅
- 초대장 발송

예산은 대략 300만원 정도 잡았어요. 혹시 놓친 부분 있으면 댓글로 알려주세요!',
  '550e8400-e29b-41d4-a716-446655440001',
  'free-talk',
  32,
  15,
  180,
  'published',
  NOW() - INTERVAL '8 hours',
  NOW() - INTERVAL '8 hours',
  NOW() - INTERVAL '8 hours'
),
(
  '650e8400-e29b-41d4-a716-446655440006',
  '아기 예방접종 일정표',
  '헷갈리는 예방접종 일정 정리해봤어요!

📅 필수 예방접종:
- 생후 1개월: BCG, B형간염 2차
- 생후 2개월: DTaP, 폴리오, Hib, 폐렴구균, 로타바이러스
- 생후 4개월: DTaP, 폴리오, Hib, 폐렴구균, 로타바이러스
- 생후 6개월: DTaP, B형간염 3차, 폐렴구균, 로타바이러스

보건소에서 무료로 맞을 수 있으니 꼭 챙기세요!',
  '550e8400-e29b-41d4-a716-446655440003',
  'health',
  28,
  9,
  210,
  'published',
  NOW() - INTERVAL '12 hours',
  NOW() - INTERVAL '12 hours',
  NOW() - INTERVAL '12 hours'
)
ON CONFLICT (id) DO NOTHING;

-- ========================
-- 4. Insert Comments
-- ========================

INSERT INTO comments (id, post_id, author_id, parent_id, content, likes_count, is_deleted, created_at) VALUES
(
  '750e8400-e29b-41d4-a716-446655440001',
  '650e8400-e29b-41d4-a716-446655440001',
  '550e8400-e29b-41d4-a716-446655440002',
  NULL,
  '저는 유모차랑 카시트 먼저 샀어요! 둘 다 필수품이라 아끼지 마세요 ㅎㅎ',
  5,
  false,
  NOW() - INTERVAL '1 day'
),
(
  '750e8400-e29b-41d4-a716-446655440002',
  '650e8400-e29b-41d4-a716-446655440001',
  '550e8400-e29b-41d4-a716-446655440003',
  NULL,
  '분유 대량 구매 추천드려요. 할인 받을 수 있어요!',
  3,
  false,
  NOW() - INTERVAL '1 day'
),
(
  '750e8400-e29b-41d4-a716-446655440003',
  '650e8400-e29b-41d4-a716-446655440002',
  '550e8400-e29b-41d4-a716-446655440001',
  NULL,
  '와 정말 유용한 정보네요! 감사합니다 ^^',
  8,
  false,
  NOW() - INTERVAL '20 hours'
),
(
  '750e8400-e29b-41d4-a716-446655440004',
  '650e8400-e29b-41d4-a716-446655440002',
  '550e8400-e29b-41d4-a716-446655440004',
  NULL,
  '혹시 서류 준비할 때 어려운 점 없으셨나요?',
  2,
  false,
  NOW() - INTERVAL '18 hours'
),
(
  '750e8400-e29b-41d4-a716-446655440005',
  '650e8400-e29b-41d4-a716-446655440003',
  '550e8400-e29b-41d4-a716-446655440002',
  NULL,
  '백색소음 정말 효과 좋아요! 저희 아기도 잘 자더라구요',
  12,
  false,
  NOW() - INTERVAL '2 hours'
),
(
  '750e8400-e29b-41d4-a716-446655440006',
  '650e8400-e29b-41d4-a716-446655440003',
  '550e8400-e29b-41d4-a716-446655440004',
  NULL,
  '저도 수면교육 시작해야 하는데... 용기 얻고 갑니다!',
  6,
  false,
  NOW() - INTERVAL '1 hour'
)
ON CONFLICT (id) DO NOTHING;

-- ========================
-- 5. Insert Sample Conversations & Messages
-- ========================

INSERT INTO conversations (id, user_id, title, conversation_type, created_at, updated_at, last_message_at) VALUES
(
  '850e8400-e29b-41d4-a716-446655440001',
  '550e8400-e29b-41d4-a716-446655440001',
  '서울 거주 첫째 출산 지원금',
  'policy_search',
  NOW() - INTERVAL '1 day',
  NOW() - INTERVAL '1 day',
  NOW() - INTERVAL '1 day'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO messages (id, conversation_id, role, content, message_type, created_at) VALUES
(
  '950e8400-e29b-41d4-a716-446655440001',
  '850e8400-e29b-41d4-a716-446655440001',
  'user',
  '서울에 살고 있는데 첫째 아이 출산하면 받을 수 있는 지원금이 뭐가 있나요?',
  'text',
  NOW() - INTERVAL '1 day'
),
(
  '950e8400-e29b-41d4-a716-446655440002',
  '850e8400-e29b-41d4-a716-446655440001',
  'assistant',
  '서울시에 거주하시는 경우 받을 수 있는 출산 지원금은 다음과 같습니다:

1. **첫만남 이용권** (전국): 200만원 바우처
2. **서울시 출산지원금**: 첫째 20만원 (서울페이)
3. **부모급여**: 0세 월 100만원, 1세 월 50만원
4. **아동수당**: 월 10만원 (8세 미만까지)

총 첫해에만 약 1,400만원 이상의 지원을 받으실 수 있습니다! 각 지원금은 별도로 신청하셔야 하니 놓치지 마세요 😊',
  'policy_result',
  NOW() - INTERVAL '1 day'
)
ON CONFLICT (id) DO NOTHING;

-- ========================
-- Success Message
-- ========================

SELECT
  'Dummy data inserted successfully! 🎉' as status,
  (SELECT COUNT(*) FROM users) as users_count,
  (SELECT COUNT(*) FROM posts) as posts_count,
  (SELECT COUNT(*) FROM comments) as comments_count,
  (SELECT COUNT(*) FROM policies) as policies_count;

-- ========================
-- Test User Credentials
-- ========================

-- Use these credentials to login:
-- Email: test1@example.com | Password: password123
-- Email: test2@example.com | Password: password123
-- Email: mommy@example.com | Password: password123
-- Email: daddy@example.com | Password: password123