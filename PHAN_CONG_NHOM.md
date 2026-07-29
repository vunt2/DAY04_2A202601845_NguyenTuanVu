# 📋 BẢNG PHÂN CÔNG DỰ ÁN LAB 04 V2 — RESEARCH AGENT TOOL EVAL

> **Dự án**: Day 04 Lab v2 — Research Agent Tool Eval  
> **Lớp / Khóa**: AI20K - Lab 04 (Evidence-driven Agent Optimization)  
> **Repository**: [DAY04_2A202601845_NguyenTuanVu](https://github.com/vunt2/DAY04_2A202601845_NguyenTuanVu)

## 1. Mục tiêu và nguyên tắc bàn giao

Nhóm xây dựng Research Agent chạy với provider thật, dùng log JSON làm bằng chứng để tối ưu routing qua `v0` → `v3`. Toàn bộ sản phẩm nộp nằm trong thư mục `starter_v0/`.

Mỗi vòng tối ưu chỉ thay đổi `starter_v0/artifacts/system_prompt.md` **hoặc** `starter_v0/artifacts/tools.yaml` theo một giả thuyết rõ ràng; sau đó chạy eval, đọc log và ghi kết quả vào version log. Không tạo ba version giống hệt nhau.

## 2. Nhánh Git thực tế và vai trò

```text
main (sản phẩm hoàn chỉnh)
 ├── feature/vu-ui-qa          — Nguyễn Tuấn Vũ: UI, report, tích hợp
 ├── feature/phong-tools-data  — Nguyễn Văn Phong: tool mới, tool declaration
 ├── feature/hung-system-prompt— Nguyễn Phúc Hưng: prompt, routing policy
 └── feature/tung-agent-loop   — Nguyễn Hữu Khánh Tùng: eval, log, QA
```

Các nhánh trong sơ đồ là tên nhánh đang tồn tại trong repository. Chỉ merge vào `main` sau khi phần việc đã được kiểm thử và không làm hỏng các artifact chung.

## 3. Phân công chi tiết

### 1. Nguyễn Tuấn Vũ — UI, Report & Integration Lead

- **Nhánh Git**: `feature/vu-ui-qa`
- **File chính**: `starter_v0/app.py`, `starter_v0/requirements.txt`, `starter_v0/artifacts/REPORT.md`, `starter_v0/artifacts/version_log.csv`
- **Nhiệm vụ**:
  1. Dựng UI Streamlit tái sử dụng `run_model_tool_loop` từ `chat.py`; không viết agent loop riêng.
  2. Hiển thị request/response, `rounds`, trace từng tool (tên, args, status, result/error), transcript/run và artifact version; cho phép so sánh cùng scenario giữa `v0`–`v3`.
  3. Lưu transcript JSON, khai báo `streamlit>=1.30.0` cùng dependency cần thiết trong `requirements.txt`, và xác nhận UI chạy được tại `http://localhost:8501`.
  4. Hoàn thiện `REPORT.md`: Phần A trước demo; Phần B sau cùng, dựa trên run log và transcript thật. Nếu cần nhóm khác truy cập, tạo và kiểm tra URL demo an toàn.
  5. Chủ trì kiểm thử tích hợp trước khi merge/nộp: không lộ secret, UI và các artifact cùng dùng đúng version.

### 2. Nguyễn Văn Phong — Tool & Tool-Declaration Developer

- **Nhánh Git**: `feature/phong-tools-data`
- **File chính**: `starter_v0/tools/<new_tool>/`, `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`
- **Nhiệm vụ**:
  1. Phát triển ít nhất một tool mới cho nhóm, gồm `tool.py` và `TOOL.md`.
  2. Đăng ký tool trong `tools/__init__.py`, thêm declaration/schema trong `artifacts/tools.yaml`, rồi smoke-test trực tiếp theo contract của tool.
  3. Hoàn thiện mô tả các tool core để nêu rõ khi nào dùng, khi nào không dùng, argument/default quan trọng và confirmation boundary cho action tool.
  4. Khi đổi tên tool, đồng bộ các chỗ liên quan: prompt, `tools.yaml`, registry, `TOOL.md`, eval và report.

> Phong là người sở hữu cấu trúc và declaration ban đầu của `tools.yaml`. Sau khi merge, Hưng chỉ sửa nội dung declaration trong các vòng tối ưu đã thống nhất để tránh conflict.

### 3. Nguyễn Phúc Hưng — System Prompt & Routing Policy Engineer

- **Nhánh Git**: `feature/hung-system-prompt`
- **File chính**: `starter_v0/artifacts/system_prompt.md`; chỉ sửa `starter_v0/artifacts/tools.yaml` khi đã thống nhất với Phong
- **Nhiệm vụ**:
  1. Đọc failed trace từ baseline và đặt giả thuyết cụ thể cho từng lỗi routing/args/boundary.
  2. Tối ưu `system_prompt.md` qua các version `v1`, `v2`, `v3`: phân biệt khi dùng `lookup`, `social_search`, `timeline`, `fetch`, `clarify` và khi không gọi tool.
  3. Thiết kế confirmation boundary cho hành vi nhạy cảm: agent phải hỏi lại/xác nhận trước action phù hợp.
  4. Mỗi lần thay đổi phải cung cấp reason, hypothesis và artifact hash cho Vũ/Tùng ghi vào `version_log.csv`.

### 4. Nguyễn Hữu Khánh Tùng — Eval, Evidence & QA Lead

- **Nhánh Git**: `feature/tung-agent-loop`
- **File chính**: `starter_v0/data/eval_group.json`, `starter_v0/runs/`, `starter_v0/analysis/`, `starter_v0/transcripts/`
- **Nhiệm vụ**:
  1. Setup provider, chạy preflight và chạy **base eval v0**; lưu run JSON, đọc ít nhất một failed trace, ghi metric baseline.
  2. Viết đúng 10 team eval cases trong `data/eval_group.json`: 5 single-turn dùng `query`, 5 multi-turn dùng `turns`; mỗi case có `id`, `phase: "B"`, `failure_type` hợp lệ, `expect` và `metadata.what_it_tests`.
  3. Chạy base eval sau từng thay đổi `v1`, `v2`, `v3`; so sánh metric với version trước, lưu run JSON và gửi evidence cho cả nhóm.
  4. Chạy group eval ở `v3`, tổng hợp run/log thành số liệu cho report; có thể dùng `analysis/` để xuất CSV phân tích.
  5. Thực hiện QA 3 live scenario: research bình thường; thiếu thông tin rồi bổ sung ở lượt sau; yêu cầu nhạy cảm kiểm tra confirmation boundary.

## 4. Trình tự thực hiện và điểm bàn giao

1. **Setup & v0** — Tùng chạy provider preflight/base eval; cả nhóm đọc trace và thống nhất lỗi ưu tiên. Vũ dựng khung UI.
2. **Tool & team eval** — Phong hoàn thiện tool mới và smoke test; Tùng hoàn thiện 10 group cases. Hai phần phải cập nhật declaration/eval đồng bộ nếu tool mới được nhắc đến.
3. **Tối ưu v1 → v3** — Hưng đề xuất một hypothesis mỗi vòng; chỉ đổi prompt hoặc declaration đã thống nhất. Tùng chạy eval và lưu evidence; Vũ ghi version log, cập nhật UI/report.
4. **Demo & report** — Cả nhóm rehearse 3–5 scenario; Vũ hoàn thiện Report A rồi Report B dựa trên evidence thật.
5. **Final gate** — Vũ chủ trì merge; Tùng kiểm tra đủ run/transcript; Phong kiểm tra tool/registry; Hưng kiểm tra prompt-routing. Nộp `starter_v0/` cùng code UI, tool mới, `version_log` v0–v3, `REPORT.md`, 10 eval cases, run JSON và transcript JSON. Không nộp `.env`, API key, `.venv` hoặc cache/build output.

## 5. Checklist hoàn thành

- [ ] Provider thật và preflight pass; có base eval `v0`.
- [ ] Ít nhất 5 tool được khai báo trong `artifacts/tools.yaml`.
- [ ] Có 3 vòng cải tiến thực chất `v1`, `v2`, `v3` và `version_log.csv` đủ bằng chứng.
- [ ] Có ít nhất 1 tool mới với `TOOL.md`, implementation, registry, declaration và smoke test.
- [ ] `eval_group.json` có đúng 10 cases: 5 single-turn, 5 multi-turn.
- [ ] UI chạy được, hiển thị trace/version và lưu transcript.
- [ ] Có run JSON, transcript JSON và `REPORT.md` hoàn chỉnh dựa trên log thật.
