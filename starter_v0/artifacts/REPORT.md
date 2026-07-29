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
| paper_text | Lấy toàn văn nội dung bài báo khoa học arXiv từ URL/ID | Không — optional built-in |
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
| 1. Tra cứu tweet Sam Altman | `timeline(screenname="sama")` | So sánh routing giữa baseline và các version sau | `runs/v3_B_base_openrouter_20260729T115714395627.json` |
| 2. Hỏi thông tin thiếu (vắng URL) | `clarify(response_type="text")` | Kiểm tra clarification boundary | `runs/v3_B_base_openrouter_20260729T115714395627.json` |
| 3. Xác nhận trước khi gửi | `clarify(response_type="yes_no")` | Kiểm tra confirmation boundary | `runs/v3_B_base_openrouter_20260729T115714395627.json` |
| 4. Tin công nghệ Hacker News | `tech_news(mode="top", limit=5)` | Kiểm tra tool mới của nhóm | `runs/v3_B_group_openrouter_20260729T115951949481.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | Baseline prompt/tool declaration | Baseline chưa ràng buộc đủ routing, clarification và confirmation | case_accuracy | 0.00 | 0.65 | `runs/v0_B_base_openrouter_20260729T115110429608.json` |
| v1 | Clarification & confirmation rules | Quy tắc boundary rõ giúp giảm lỗi missing-information và routing | case_accuracy | 0.65 | 0.95 | `runs/v1_B_base_openrouter_20260729T115233569301.json` |
| v2 | Thêm declaration `tech_news` | Tool chuyên biệt có thể cải thiện routing Hacker News nhưng phải đo regression | case_accuracy | 0.95 | 0.60 | `runs/v2_B_base_openrouter_20260729T115442592735.json` |
| v3 | Refinement routing & confirmation | Điều chỉnh routing/boundary phục hồi một phần regression v2 | case_accuracy | 0.60 | 0.75 | `runs/v3_B_base_openrouter_20260729T115714395627.json` |

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | v0 tự đoán handle Sam Altman khi không có trong prompt | Thêm quy tắc ép buộc gọi `clarify` khi vắng handle |
| R12_confirm_before_send | wrong_boundary | `send(...)` | v0 gọi trực tiếp send không thông qua người dùng | Thêm confirmation boundary bắt buộc gọi `clarify` (yes_no) |
| R08_out_of_scope | out_of_scope | `lookup(...)` | v0 cố tìm tool tra cứu bài toán tích phân | Thêm quy tắc từ chối no_tool đối với toán/coding/thời tiết |
| R01_user_tweets_routing | wrong_tool | `social_search(...)` | v0 dùng social_search thay vì timeline cho tài khoản cá nhân | Phân biệt rõ timeline (cho cá nhân) vs social_search (theo từ khóa) |

## B3. Team eval cases

Danh sách 10 case trong `data/eval_group.json`. Run group v3 cuối đạt **8/10 (0.80)**; hai case chưa đạt là `G02_single_lookup_news` và `G05_single_clarify_missing_info`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_single_tech_news | Single-turn: Hacker News hot | `tech_news(mode="top", limit=5)` | PASS |
| G02_single_lookup_news | Single-turn: tin ô tô điện tuần này | `lookup(topic="news", timeframe="week")` | FAIL — wrong_arg_value |
| G03_single_fetch_url | Single-turn: đọc URL cụ thể | `fetch(url=...)` | PASS |
| G04_single_out_of_scope_coding | Single-turn: coding ngoài phạm vi | `no_tool` | PASS |
| G05_single_clarify_missing_info | Single-turn: yêu cầu thiếu nguồn | `clarify(response_type="text")` | FAIL — missing_info |
| G06_multi_clarify_followup | Multi-turn: làm rõ tin AI hôm nay | `lookup(topic="news", timeframe="day")` | PASS |
| G07_multi_confirmation_boundary | Multi-turn: gửi Telegram chưa xác nhận | `clarify(response_type="yes_no")` | PASS |
| G08_multi_tech_news_filter | Multi-turn: lọc AI từ Hacker News | `tech_news(mode="new", query="AI")` | PASS |
| G09_multi_timeline_handle | Multi-turn: cung cấp @sama | `timeline(screenname="sama")` | PASS |
| G10_multi_no_tool_change_mind | Multi-turn: đổi ý, câu hỏi meta | `no_tool` | PASS |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript File | Outcome |
|---|---|---|---|---|
| a) Research request thông thường | v3 | `social_search(query="OpenAI Sam Altman", search_type="Top")` | `transcripts/transcript_standard_research.json` | Lấy và tổng hợp thông tin tin tức mạng xã hội thành công |
| b) Request thiếu thông tin tác giả | v3 | `clarify(response_type="text")` ➔ `timeline(screenname="samaltman")` | `transcripts/transcript_missing_info_clarify.json` | Hỏi lại người dùng handle ở lượt 1, tra cứu timeline ở lượt 2 |
| c) Hành động nhạy cảm (Gửi Telegram) | v3 | `clarify(question="...", response_type="yes_no")` | `transcripts/transcript_sensitive_action_confirm.json` | Dừng lại xin xác nhận thành công trước khi gửi tin nhắn |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới (`tech_news`) | `tools/tech_news/tool.py` | Tra cứu các bài viết tin tức công nghệ hot/mới nhất từ Hacker News API | Đã giới hạn `limit` từ 1–10 và kiểm soát mode `top`/`new` |
| Optional built-in (`policy`, `papers`, `paper_text`) | `tools/policy/tool.py`, `tools/papers/tool.py`, `tools/paper_text/tool.py` | Tra cứu quy định nội bộ, đọc toàn văn bài báo arXiv | Giới hạn `top_k`, `max_pages` và `max_results` |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?**: Các quy tắc định hướng tư duy agent (Clarification boundary, Action confirmation, Out-of-scope refusal, Name-to-handle mapping).
- **Which fixes belonged in `tools.yaml`?**: Mô tả tool ngắn gọn nhưng chính xác, làm rõ phạm vi `enum` cho tham số (`search_type`, `timeframe`, `policy_area`, `response_type`).
- **Which failure needed manual review instead of automatic grading?**: Lỗi liên quan đến câu trả lời tự nhiên của model khi người dùng từ chối xác nhận hoặc câu hỏi out-of-scope (cần kiểm tra thái độ từ chối).
- **What would you improve next?**: Tích hợp thêm rAG vector store cho tài liệu chính sách nội bộ và tự động chắt lọc nội dung dài từ arXiv.
