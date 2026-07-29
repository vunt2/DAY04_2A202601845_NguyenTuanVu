# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team: Day 04 Research Agent Team (Nhóm 4)
- Members:
  1. Nguyễn Tuấn Vũ (MSSV: 2A202601845 - Trưởng nhóm / UI & Report Lead)
  2. Nguyễn Phúc Hưng (MSSV: 2A202601115 - Prompt & Policy Engineer)
  3. Nguyễn Văn Phong (MSSV: 2A202601087 - Tool Developer)
  4. Nguyễn Hữu Khánh Tùng (MSSV: 2A202601781 - Eval & Benchmark QA)
- Provider/model: OpenRouter / OpenAI / Gemini (Configurable)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent: hỗ trợ tìm kiếm tin tức mạng xã hội theo từ khóa (`social_search`), tra cứu bài đăng theo tài khoản (`timeline`), đọc và trích xuất nội dung URL (`fetch`), tra cứu web (`lookup`), hỏi lại thông tin khi mơ hồ (`clarify`), định dạng dữ liệu (`format`), và hỗ trợ tra cứu tài liệu khoa học arXiv / chính sách nội bộ.

**Link dùng thử (truy cập được trong showdown):**

> URL: http://localhost:8501

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận | không |
| timeline | lấy các bài đăng gần đây của tài khoản mạng xã hội | không |
| social_search | tìm bài đăng mạng xã hội theo từ khóa | không |
| lookup | tra cứu thông tin tổng hợp trên internet | không |
| fetch | đọc và trích xuất nội dung từ một địa chỉ URL | không |
| format | trình bày các dữ liệu thu thập thành văn bản markdown | không |
| send | gửi tin nhắn thông báo (có confirmation boundary) | không |
| policy | tra cứu tài liệu chính sách công ty nội bộ | không |
| papers | tìm kiếm bài báo khoa học trên arXiv | không |
| paper_text | tải và trích xuất text nội dung từ arXiv PDF | không |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## A4. Kịch bản demo đã rehearse

> Chuẩn bị 3–5 scenario. Mỗi scenario cần cho thấy tool đã làm gì và một thay đổi cụ thể giữa các version.

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

This section is for the mandatory team-authored eval set. Optional built-ins do
not belong here.

File template để trống có chủ đích; nhóm phải tự thiết kế đủ 10 case.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên |  |  |  |
| Optional built-in |  |  |  |
| Bonus: tool mới thứ 4 trở đi |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
