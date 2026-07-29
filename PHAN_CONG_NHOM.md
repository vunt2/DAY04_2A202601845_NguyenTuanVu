# 📋 BẢNG PHÂN CÔNG DỰ ÁN LAB 04 V2 — RESEARCH AGENT TOOL EVAL
> **Dự án**: Day 04 Lab v2 — Research Agent Tool Eval  
> **Lớp / Khóa**: AI20K - Lab 04 (Evidence-driven Agent Optimization)  
> **Repository**: [DAY04_2A202601845_NguyenTuanVu](https://github.com/vunt2/DAY04_2A202601845_NguyenTuanVu)

---

## 🎯 1. MỤC TIÊU DỰ ÁN DAY 04 (RESEARCH AGENT)
Xây dựng một **Research Agent (Agent nghiên cứu thông tin)** chạy thực tế với vòng lặp cải tiến bằng bằng chứng (Evidence-driven optimization):
1. **Chạy Baseline (v0)** với API provider thật.
2. **Đánh giá Log & Fix lỗi**: Sửa `artifacts/system_prompt.md` và `artifacts/tools.yaml` qua các phiên bản `v1`, `v2`, `v3`.
3. **Phát triển Tool mới**: Viết thêm ít nhất 1 Tool mới trong `tools/` (kèm `TOOL.md`, đăng ký trong `tools/__init__.py` và `artifacts/tools.yaml`).
4. **Bộ Eval Case Nhóm**: Thiết kế 10 câu eval case nhóm trong `data/eval_group.json` (5 câu single-turn + 5 câu multi-turn).
5. **Giao diện UI (Streamlit `app.py`)**: Tái sử dụng `chat.py`, hiển thị trace công cụ, transcript và so sánh kết quả qua các version `v0 ➔ v3`.
6. **Báo cáo**: Hoàn thiện tài liệu nghiệm thu `artifacts/REPORT.md`.

---

## 👥 2. PHÂN CÔNG VAI TRÒ & NHÁNH GIT 4 THÀNH VIÊN

```text
main (Nhánh chính - Sản phẩm hoàn chỉnh)
 ├── 🌿 feature/vu-ui-report       (Nguyễn Tuấn Vũ - UI & Report Lead)
 ├── 🌿 feature/phong-tools-extension (Nguyễn Văn Phong - Tool Developer)
 ├── 🌿 feature/hung-system-prompt (Nguyễn Phúc Hưng - Prompt Engineer)
 └── 🌿 feature/tung-eval-qa       (Nguyễn Hữu Khánh Tùng - Eval & Benchmark QA)
```

---

## 📋 3. CHI TIẾT NHIỆM VỤ & FILE TÁC ĐỘNG THEO TỪNG THÀNH VIÊN

### 👤 1. NGUYỄN TUẤN VŨ (Trưởng nhóm — UI & Report Lead)
* **Nhánh Git**: `feature/vu-ui-report` (tương ứng `feature/vu-ui-qa`)
* **File tác động chính**: `app.py`, `artifacts/REPORT.md`, `artifacts/version_log.csv`
* **Nhiệm vụ cụ thể**:
  - **Giai đoạn 1**: Thiết kế giao diện **Streamlit** (`app.py`) hiển thị chat, trace của từng tool (args, status, result), và chọn version (`v0`, `v1`, `v2`, `v3`).
  - **Giai đoạn 2**: Ghi nhận nhật ký cải tiến trong `artifacts/version_log.csv`.
  - **Giai đoạn 3**: Hoàn thiện báo cáo `artifacts/REPORT.md` (Phần A trước demo, Phần B trước khi nộp bài).

---

### 👤 2. NGUYỄN VĂN PHONG (Tool & Extension Developer)
* **Nhánh Git**: `feature/phong-tools-data` (hoặc `feature/phong-tools-extension`)
* **File tác động chính**: `tools/<new_tool>/`, `tools/__init__.py`, `artifacts/tools.yaml`
* **Nhiệm vụ cụ thể**:
  - **Giai đoạn 1**: Tối ưu khai báo các tool sẵn có (`clarify`, `timeline`, `social_search`, `lookup`, `fetch`, `format`) trong `artifacts/tools.yaml` (thêm description rõ khi nào dùng / không dùng).
  - **Giai đoạn 2**: Phát triển **1 Tool mới cho nhóm** (ví dụ: `finance_news`, `arxiv_summary` hoặc `code_search`), kèm file `TOOL.md` và mã nguồn Python.
  - **Giai đoạn 3**: Đăng ký tool mới vào `tools/__init__.py` và `artifacts/tools.yaml`.

---

### 👤 3. NGUYỄN PHÚC HƯNG (System Prompt & Policy Engineer)
* **Nhánh Git**: `feature/hung-system-prompt`
* **File tác động chính**: `artifacts/system_prompt.md`
* **Nhiệm vụ cụ thể**:
  - **Giai đoạn 1**: Phân tích lỗi từ v0 baseline, tiến hành tối ưu file `artifacts/system_prompt.md` qua các phiên bản `v1`, `v2`, `v3`.
  - **Giai đoạn 2**: Định nghĩa rõ ràng quy tắc Routing cho từng loại intent: khi nào `lookup`, khi nào `social_search`, khi nào `clarify`.
  - **Giai đoạn 3**: Xây dựng rào chắn xác nhận (Confirmation Boundary) đối với các hành vi nhạy cảm (như tool `send`).

---

### 👤 4. NGUYỄN HỮU KHÁNH TÙNG (Eval & Benchmark QA)
* **Nhánh Git**: `feature/tung-agent-loop` (hoặc `feature/tung-eval-qa`)
* **File tác động chính**: `data/eval_group.json`, `run_eval.py`
* **Nhiệm vụ cụ thể**:
  - **Giai đoạn 1**: Thiết kế bộ **10 Eval cases của nhóm** trong `data/eval_group.json` (5 câu single-turn + 5 câu multi-turn).
  - **Giai đoạn 2**: Thực thi công cụ đánh giá `python run_eval.py` để chấm điểm tỷ lệ chính xác (Pass rate) qua các version `v0`, `v1`, `v2`, `v3`.
  - **Giai đoạn 3**: Thu thập run JSON log và tổng hợp số liệu cho nhóm.

---

## ⏳ 4. QUY TRÌNH THỰC HIỆN DỰ ÁN (WORKFLOW)

1. **Bước 1 (v0 Baseline)**: Chạy eval nền tảng với `starter_v0`.
2. **Bước 2 (Viết Tool & Eval)**: Bạn Phong viết Tool mới, bạn Tùng hoàn thiện `data/eval_group.json`.
3. **Bước 3 (Tối ưu Prompt & Schema)**: Bạn Hưng chỉnh sửa `system_prompt.md` và `tools.yaml` (v1 -> v2 -> v3).
4. **Bước 4 (Dựng UI & Báo cáo)**: Bạn Vũ hoàn thiện `app.py` Streamlit và `artifacts/REPORT.md`.
5. **Bước 5 (Merge & Nộp)**: Merge tất cả về `main` và kiểm thử tích hợp.
