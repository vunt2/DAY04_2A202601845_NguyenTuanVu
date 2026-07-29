from __future__ import annotations

import json
from typing import Any
from providers.base import ModelResponse, ToolCall


class MockProvider:
    """Mock Provider offline cho demo Streamlit khi chưa điền API key thực tế."""

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        # Kiểm tra nếu lượt trước đã gọi tool và có kết quả (TOOL_RESULTS_JSON) ➔ Dừng vòng lặp và trả về câu trả lời cuối
        last_msg = messages[-1].get("content", "") if messages else ""
        if "TOOL_RESULTS_JSON:" in last_msg:
            return ModelResponse(
                text="Đã thu thập và xử lý xong dữ liệu! Bạn có thể bấm mở khung 'Executed Tool Traces (Rounds & Events)' ở trên để xem chi tiết kết quả trả về của Tool.",
                tool_calls=[]
            )

        user_text = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_text = m.get("content", "").lower()
                break

        # Route offline tool decision based on query intent
        if "sam altman" in user_text or "openai" in user_text:
            return ModelResponse(
                text="Tôi sẽ tìm kiếm tin tức trên mạng xã hội về OpenAI và Sam Altman.",
                tool_calls=[ToolCall("social_search", {"query": "OpenAI Sam Altman"})]
            )
        elif "samaltman" in user_text or "timeline" in user_text:
            return ModelResponse(
                text="Tôi sẽ lấy danh sách bài đăng gần đây của tài khoản samaltman.",
                tool_calls=[ToolCall("timeline", {"screenname": "samaltman"})]
            )
        elif "tác giả này" in user_text or "thiếu" in user_text:
            return ModelResponse(
                text="Bạn muốn tổng hợp bài viết của tác giả nào ạ? Vui lòng cung cấp tên tài khoản.",
                tool_calls=[ToolCall("clarify", {"question": "Bạn muốn tổng hợp bài viết của tài khoản nào?"})]
            )
        elif "transformer" in user_text or "arxiv" in user_text or "bài báo" in user_text:
            return ModelResponse(
                text="Tôi sẽ tìm các bài báo khoa học về Transformer trên arXiv.",
                tool_calls=[ToolCall("papers", {"query": "Transformer LLM"})]
            )
        elif "công nghệ" in user_text or "tech news" in user_text or "tin tức" in user_text:
            return ModelResponse(
                text="Tôi sẽ tra cứu tin tức công nghệ mới nhất.",
                tool_calls=[ToolCall("tech_news", {"query": "technology"})]
            )
        elif "telegram" in user_text or "gửi" in user_text:
            return ModelResponse(
                text="Vui lòng xác nhận bạn có muốn gửi bản tổng hợp này lên kênh Telegram không?",
                tool_calls=[ToolCall("send", {"text": "Bản tổng hợp tin tức AI", "confirmed": False})]
            )
        else:
            return ModelResponse(
                text="Chào bạn! Tôi là Research Agent hỗ trợ tìm kiếm tin tức, đọc bài báo khoa học và tra cứu thông tin.",
                tool_calls=[]
            )
