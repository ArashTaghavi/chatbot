from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_date() -> str:
    return datetime.now(ZoneInfo("Asia/Tehran")).strftime("%Y-%m-%d %H:%M:%S")


# سفارش‌های آزمایشی
orders = {
    "1001": "pending",
    "1002": "shipped",
    "1003": "pending",
}

# ارتباط محصول با شماره سفارش
products = {
    "لپ تاپ": "1001",
    "موبایل": "1002",
    "هدفون": "1003",
}


def find_order_id(product_name: str) -> str:
    return products.get(product_name, "سفارشی پیدا نشد.")


def cancel_order(order_id: str) -> str:
    if order_id not in orders:
        return f"سفارش {order_id} پیدا نشد."

    if orders[order_id] == "cancelled":
        return f"سفارش {order_id} قبلاً لغو شده است."

    if orders[order_id] != "pending":
        return f"سفارش {order_id} قابل لغو نیست."

    orders[order_id] = "cancelled"

    return f"سفارش {order_id} با موفقیت لغو شد."


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "دریافت تاریخ و ساعت فعلی ایران",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_order_id",
            "description": (
                "پیدا کردن شماره سفارش بر اساس نام محصول. "
                "اگر شماره سفارش مشخص نیست، ابتدا از این ابزار استفاده کن. "
                "شماره سفارش را حدس نزن."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "نام محصول سفارش داده شده",
                    }
                },
                "required": ["product_name"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": (
                "لغو سفارش مشتری با دریافت شماره سفارش. "
                "اگر شماره سفارش مشخص نیست، ابتدا find_order_id را اجرا کن."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "شماره سفارش معتبر",
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    },
]
