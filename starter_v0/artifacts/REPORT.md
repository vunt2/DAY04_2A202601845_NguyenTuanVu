# Day 04 Lab v2 Report — Research Agent

## Team

- **Team**: DAY04_2A202601845_NguyenTuanVu (Nhóm 4)
- **Members**:
  1. Nguyễn Tuấn Vũ (MSSV: 2A202601845 - Trưởng nhóm / UI & Report Lead)
  2. Nguyễn Phúc Hưng (MSSV: 2A202601115 - Prompt & Policy Engineer)
  3. Nguyễn Văn Phong (MSSV: 2A202601087 - Tool Developer)
  4. Nguyễn Hữu Khánh Tùng (MSSV: 2A202601781 - Eval & Benchmark QA)
- **Provider/model**: OpenRouter / `openai/gpt-4o-mini`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent chuyên sâu hỗ trợ tra cứu thông tin đa nguồn (Web, Twitter/Social, bài báo khoa học arXiv, tài liệu chính sách nội bộ, tin tức công nghệ Hacker News), đọc nội dung URL/arXiv toàn văn, hỏi làm rõ khi thiếu thông tin và xin xác nhận trước khi thực hiện hành động ghi/gửi.

**Link dùng thử (truy cập được trong showdown):**
- URL: `http://localhost:8501` (Streamlit UI local demo)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin hoặc xin xác nhận trước khi gửi | Không |
| timeline | Lấy các bài đăng gần đây của tài khoản cụ thể (sama, elonmusk, karpathy) | Không |
| social_search | Tìm kiếm bài đăng trên mạng xã hội theo từ khóa (Latest/Top) | Không |
| lookup | Tra cứu tin tức (topic=news) hoặc thông tin chung trên web | Không |
| fetch | Lấy nội dung chi tiết từ một đường dẫn URL | Không |
| format | Trình bày dữ liệu đã thu thập thành báo cáo digest | Không |
| send | Gửi văn bản báo cáo ra kênh ngoài | Không |
| policy | Tra cứu quy định & chính sách nội bộ công ty | Không |
| papers | Tìm kiếm bài báo khoa học trên arXiv | Không |
| paper_text | Lấy toàn văn nội dung bài báo khoa học arXiv từ URL/ID | Có (Nhóm phát triển) |
| tech_news | Lấy tin tức công nghệ hot/mới từ Hacker News | Có (Nhóm phát triển) |

## A3. Câu hỏi mẫu để thử

1. "Tweet mới nhất của Sam Altman là gì?"
2. "Tìm giúp mình bài báo khoa học mới nhất về LLM reasoning trên arXiv"
3. "Chính sách công ty về data privacy quy định như thế nào?"
4. "Tóm tắt bài viết này hộ mình" *(Agent sẽ gọi clarify hỏi lại URL)*
5. "Gửi bản tin này vào Telegram giúp mình" *(Agent sẽ gọi clarify để hỏi xác nhận yes/no)*

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| 1. Tra cứu tweet Sam Altman | `timeline(screenname="sama")` | v0 đoán bừa/gọi nhầm tool -> v3 map đúng handle `sama` | `runs/v3_B_base_openrouter_*.json` |
| 2. Hỏi thông tin thiếu (vắng URL) | `clarify(response_type="text")` | v0 đoán đại URL -> v3 hỏi lại người dùng lịch sự | `runs/v3_B_base_openrouter_*.json` |
| 3. Xác nhận trước khi gửi | `clarify(response_type="yes_no")` | v0 tự gửi nguy hiểm -> v3 có confirmation boundary | `runs/v3_B_base_openrouter_*.json` |
| 4. Tìm bài báo khoa học arXiv | `papers(query="LLM reasoning")` | v0 tìm web chung -> v3 dùng đúng arXiv tools | `runs/v3_B_group_openrouter_*.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | Baseline prompt | Baseline prompt đoán mò tham số và bỏ qua boundary | case_accuracy | 0.00 | 0.70 | `runs/v0_B_base_openrouter_20260729T103434443875.json` |
| v1 | Thêm quy tắc clarify & confirmation boundary | Quy tắc clarify rõ ràng giúp giảm lỗi missing_info và wrong_boundary | case_accuracy | 0.70 | 0.85 | `runs/v1_B_base_openrouter_20260729T105303966979.json` |
| v2 | Tối ưu routing timeline, search & mapping handle | Định nghĩa rõ mapping handle (sama, elonmusk) và timeframe giải quyết wrong_tool/args | case_accuracy | 0.85 | 0.95 | `runs/v2_B_base_openrouter_20260729T105303979726.json` |
| v3 | Tinh chỉnh prompt multi-turn & bổ sung group tools | Prompt v3 hoàn chỉnh xử lý 100% case base và 100% case group | case_accuracy | 0.95 | 1.00 | `runs/v3_B_base_openrouter_20260729T105303980713.json` |

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | v0 tự đoán handle Sam Altman khi không có trong prompt | Thêm quy tắc ép buộc gọi `clarify` khi vắng handle |
| R12_confirm_before_send | wrong_boundary | `send(...)` | v0 gọi trực tiếp send không thông qua người dùng | Thêm confirmation boundary bắt buộc gọi `clarify` (yes_no) |
| R08_out_of_scope | out_of_scope | `lookup(...)` | v0 cố tìm tool tra cứu bài toán tích phân | Thêm quy tắc từ chối no_tool đối với toán/coding/thời tiết |
| R01_user_tweets_routing | wrong_tool | `social_search(...)` | v0 dùng social_search thay vì timeline cho tài khoản cá nhân | Phân biệt rõ timeline (cho cá nhân) vs social_search (theo từ khóa) |

## B3. Team eval cases

Danh sách 10 case trong `data/eval_group.json`:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_arxiv_paper_search | Single-turn: Tìm bài báo khoa học | `papers(query="LLM reasoning")` | PASS |
| G02_company_policy_lookup | Single-turn: Tra cứu quy định nội bộ | `policy(query="data privacy", policy_area="data_privacy")` | PASS |
| G03_missing_arxiv_id | Single-turn: Đọc bài báo nhưng vắng arXiv URL | `clarify(response_type="text")` | PASS |
| G04_out_of_scope_weather | Single-turn: Dự báo thời tiết ngoài phạm vi | `no_tool` (refuse) | PASS |
| G05_confirm_telegram_send | Single-turn: Gửi báo cáo qua Telegram | `clarify(response_type="yes_no")` | PASS |
| GM01_clarify_then_search_paper | Multi-turn: Lượt 1 thiếu thông tin, lượt 2 bổ sung chủ đề | `papers(query="Quantum Computing")` | PASS |
| GM02_carryover_search_topic | Multi-turn: Giữ nguyên timeframe=week/topic=news | `lookup(query="DeepSeek", topic="news", timeframe="week")` | PASS |
| GM03_clarify_arxiv_url | Multi-turn: Cung cấp link arXiv ở lượt 2 | `paper_text(arxiv_url="https://arxiv.org/abs/2401.00001")` | PASS |
| GM04_correction_search_type | Multi-turn: Đổi search_type từ Latest sang Top | `social_search(query="Claude 3.5", search_type="Top")` | PASS |
| GM05_switch_tool_to_policy | Multi-turn: Chuyển đổi từ web search sang policy tool | `policy(query="AI research", policy_area="ai_research")` | PASS |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Outcome |
|---|---|---|---|
| Tweet Sam Altman | v3 | `timeline(screenname="sama")` | Lấy chính xác 5 tweet mới nhất của Sam Altman |
| Đọc bài viết không kèm link | v3 | `clarify(question="Bạn có thể cung cấp URL...", response_type="text")` | Hỏi lại URL từ người dùng thành công |
| Gửi tin Telegram | v3 | `clarify(question="Bạn có muốn gửi báo cáo này...", response_type="yes_no")` | Dừng lại xin xác nhận thành công trước khi phát hành |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới (`paper_text`) | `tools/paper_text/tool.py` | Trích xuất nội dung toàn văn bài báo từ arXiv URL | Đã bổ sung giới hạn `max_pages` và `max_chars` tránh quá tải |
| Optional built-in (`policy`, `papers`) | `tools/policy/tool.py`, `tools/papers/tool.py` | Tra cứu quy định nội bộ và tìm bài báo arXiv | Giới hạn `top_k` và `max_results` |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?**: Các quy tắc định hướng tư duy agent (Clarification boundary, Action confirmation, Out-of-scope refusal, Name-to-handle mapping).
- **Which fixes belonged in `tools.yaml`?**: Mô tả tool ngắn gọn nhưng chính xác, làm rõ phạm vi `enum` cho tham số (`search_type`, `timeframe`, `policy_area`, `response_type`).
- **Which failure needed manual review instead of automatic grading?**: Lỗi liên quan đến câu trả lời tự nhiên của model khi người dùng từ chối xác nhận hoặc câu hỏi out-of-scope (cần kiểm tra thái độ từ chối).
- **What would you improve next?**: Tích hợp thêm rAG vector store cho tài liệu chính sách nội bộ và tự động chắt lọc nội dung dài từ arXiv.
