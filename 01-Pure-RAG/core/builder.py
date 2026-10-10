import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from .tools import cancel_order, find_order_id, get_current_date, tools

load_dotenv(Path(__file__).resolve().parent / ".env")


class Builder:
    def __init__(
        self,
        retrieved_documents: list[dict],
        model: str = "gpt-4o-mini",
        summary_threshold: int = 10,
        keep_recent: int = 2,
    ) -> None:
        self.client = OpenAI()
        self.retrieved_documents = retrieved_documents
        self.model = model

        self.chat_history: list[ChatCompletionMessageParam] = []
        self.chat_summary = ""

        self.summary_threshold = summary_threshold
        self.keep_recent = keep_recent

    def _build_context(self) -> str:
        return "\n".join(document["text"] for document in self.retrieved_documents)

    def _build_prompt(self) -> str:
        return f"""
تو یک دستیار هوش مصنوعی برای فروشگاه هستی.
وظیفه تو پاسخ‌گویی به سؤالات کاربران بر اساس [قوانین] و رعایت [ملاحظات] است.

[قوانین]:
{self._build_context()}

[ملاحظات]:
- اگر کاربر سلام و احوال‌پرسی کرد یا خودش را معرفی کرد، دوستانه پاسخ بده.
- اگر پاسخ مرتبطی در قوانین وجود نداشت، اطلاعات را حدس نزن و کاربر را به پشتیبانی ارجاع بده.
- هیچ قانون، قیمت یا شرایطی را از خودت تولید نکن.
- از خلاصه و تاریخچه مکالمه برای درک بهتر سؤال فعلی استفاده کن.
- خلاصه و تاریخچه مکالمه منبع قوانین فروشگاه نیستند.
- برای دریافت تاریخ و ساعت فعلی از ابزار get_current_date استفاده کن.
- پاسخ‌ها را کوتاه، واضح و مرتبط نگه دار.
""".strip()

    def answer(self, query):
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self._build_prompt()},
        ]

        if self.chat_summary:
            messages.append(
                {
                    "role": "system",
                    "content": f"خلاصه مکالمات قبلی:\n{self.chat_summary}",
                }
            )

        messages.extend(self.chat_history)

        user_message: ChatCompletionMessageParam = {
            "role": "user",
            "content": query,
        }

        messages.append(user_message)
        self.chat_history.append(user_message)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        max_tool_rounds = 5
        tool_round = 0

        while response.choices[0].message.tool_calls:
            if tool_round >= max_tool_rounds:
                result = "تعداد مراحل اجرای ابزار از حد مجاز بیشتر شد."
                self.chat_history.append({"role": "assistant", "content": result})
                self.summarize_history()
                return result

            assistant_message = response.choices[0].message
            tool_call_message = assistant_message.model_dump(exclude_none=True)

            messages.append(tool_call_message)
            self.chat_history.append(tool_call_message)

            for tool_call in assistant_message.tool_calls:
                if tool_call.function.name == "get_current_date":
                    tool_result = get_current_date()

                elif tool_call.function.name == "cancel_order":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        tool_result = cancel_order(args["order_id"])
                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                        tool_result = f"خطا در ورودی ابزار: {e}"

                elif tool_call.function.name == "find_order_id":
                    args = json.loads(tool_call.function.arguments)
                    tool_result = find_order_id(args["product_name"])

                else:
                    tool_result = f"ابزار {tool_call.function.name} شناخته نشد."

                tool_message: ChatCompletionMessageParam = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result),
                }

                messages.append(tool_message)
                self.chat_history.append(tool_message)

            tool_round += 1

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )

        result = response.choices[0].message.content or ""

        self.chat_history.append({"role": "assistant", "content": result})

        self.summarize_history()

        return result

    def summarize_history(self) -> None:
        if len(self.chat_history) < self.summary_threshold:
            return

        # نگهداری آخرین مکالمات کامل، همراه با Tool Callهای آن‌ها
        user_indices = [
            i
            for i, message in enumerate(self.chat_history)
            if message["role"] == "user"
        ]

        keep_turns = max(1, self.keep_recent // 2)

        if len(user_indices) <= keep_turns:
            return

        split_index = user_indices[-keep_turns]
        old_messages = self.chat_history[:split_index]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "تاریخچه مکالمه را به فارسی خلاصه کن. "
                        "اطلاعات مهم، درخواست‌های کاربر و موضوعات مطرح‌شده را حفظ کن. "
                        "خلاصه قبلی را با پیام‌های جدید ترکیب کن. "
                        "هیچ اطلاعات جدیدی اضافه نکن."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"[خلاصه قبلی]:\n{self.chat_summary}\n\n"
                        f"[پیام‌های قدیمی که باید خلاصه شوند]:\n"
                        f"{json.dumps(old_messages, ensure_ascii=False)}"
                    ),
                },
            ],
        )

        new_summary = response.choices[0].message.content

        if new_summary:
            self.chat_summary = new_summary
            self.chat_history = self.chat_history[split_index:]

    def get_messages(self):
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self._build_prompt()},
        ]

        if self.chat_summary:
            messages.append(
                {
                    "role": "system",
                    "content": f"خلاصه مکالمات قبلی:\n{self.chat_summary}",
                }
            )

        messages.extend(self.chat_history)

        return messages
