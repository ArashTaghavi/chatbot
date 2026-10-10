from html import escape

from IPython.display import HTML, display


def init_style():
    display(HTML("""
        <link
            href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css"
            rel="stylesheet"
        />

        <style>
            body {
                font-family: Vazirmatn, sans-serif !important;
                direction: rtl;
            }

            body * {
                font-family: inherit;
            }
        </style>
    """))


def chat_print(text, role="assistant"):
    is_user = role == "user"

    align = "flex-end" if is_user else "flex-start"
    bg = "#2b5278" if is_user else "#2f2f2f"

    formatted_text = escape(text).replace("\n", "<br>")

    display(HTML(f"""
            <div style="
                display: flex;
                justify-content: {align};
                margin: 8px 0;
            ">
                <div style="
                    max-width: 75%;
                    background: {bg};
                    padding: 10px 14px;
                    border-radius: 12px;
                    font-size: 14px;
                    line-height: 1.8;
                    direction: rtl;
                    text-align: right;
                ">
                    {formatted_text}
                </div>
            </div>
            """))


def loading():
    return display(
        HTML("""
        <style>
            @keyframes blink {
                0%, 80%, 100% { opacity: 0.2; }
                40% { opacity: 1; }
            }

            .typing-dot {
                display: inline-block;
                font-size: 22px;
                animation: blink 1.4s infinite;
            }

            .typing-dot:nth-child(2) {
                animation-delay: 0.2s;
            }

            .typing-dot:nth-child(3) {
                animation-delay: 0.4s;
            }
        </style>

        <div style="
            display: flex;
            justify-content: flex-start;
            margin: 8px 0;
        ">
            <div style="
                background: #2f2f2f;
                padding: 8px 16px;
                border-radius: 12px;
            ">
                <span class="typing-dot">●</span>
                <span class="typing-dot">●</span>
                <span class="typing-dot">●</span>
            </div>
        </div>
        """),
        display_id=True,
    )


def found_rules(retrieved_documents: list[dict]):
    rows = ""

    for item in retrieved_documents:
        document = escape(str(item["text"]))
        similarity = float(item["score"])

        rows += f"""
            <tr>
                <td>{document}</td>
                <td>{similarity:.4f}</td>
            </tr>
        """

    display(HTML(f"""
        <table dir="rtl" style="
            width: 100%;
            border-collapse: collapse;
            text-align: right;
        ">
            <thead style="background: #e2e8f0; color: #1e293b;">
                <tr>
                    <th style="padding: 12px;">Document</th>
                    <th style="padding: 12px;">Similarity</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>

        <style>
            td {{
                padding: 10px 12px;
                border-bottom: 1px solid #e2e8f0;
            }}
        </style>
    """))


def show_summary(summary: str):
    display(HTML(f"""
        <div dir="rtl" style="
            width: 100%;
            text-align: right;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
        ">
            <div style="
                background: #e2e8f0;
                color: #1e293b;
                padding: 12px;
                font-weight: bold;
            ">
                خلاصه چت
            </div>

            <div style="
                padding: 12px;
                line-height: 1.9;
                white-space: pre-wrap;
            ">{escape(summary)}</div>
        </div>
    """))


def show_history(messages, title: str = "تاریخچه چت"):
    rows = ""

    for index, message in enumerate(messages, start=1):
        role = escape(str(message["role"]))
        content = message.get("content") or ""

        if message.get("tool_calls"):
            tool_names = [tool["function"]["name"] for tool in message["tool_calls"]]
            content = f"Tool Call: {', '.join(tool_names)}"

        elif role == "tool":
            content = f"Tool Result: {content}"

        content = escape(str(content))

        rows += f"""
            <tr>
                <td>{index}</td>
                <td>{role}</td>
                <td style="white-space: pre-wrap;">{content}</td>
            </tr>
        """

    display(HTML(f"""
        <div dir="rtl" style="width:100%; text-align:right;">
            <div style="
                background:#e2e8f0;
                color:#1e293b;
                padding:12px;
                font-weight:bold;
                border-radius:8px 8px 0 0;
            ">
                {escape(title)}
            </div>

            <table style="
                width:100%;
                border-collapse:collapse;
                text-align:right;
            ">
                <thead style="background:#f1f5f9; color:#1e293b;">
                    <tr>
                        <th style="padding:10px;">#</th>
                        <th style="padding:10px;">Role</th>
                        <th style="padding:10px;">Content</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    """))
