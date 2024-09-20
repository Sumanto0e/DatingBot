from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.callback_data import (
    CallbackData,
)


action_keyboard = CallbackData("questionnaire", "action", "target_id")
action_keyboard_monitoring = CallbackData(
    "questionnaire_monitoring", "action", "target_id"
)
action_reciprocity_keyboard = CallbackData("questionnaire", "action", "user_for_like")
action_report_keyboard = CallbackData("report", "action", "target_id")

async def stopped_keyboard(
        target_id: int, monitoring: bool = False
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardButton(
        text=("💤 Berhenti"),
        callback_data=action_keyboard.new(action="stopped", target_id=target_id),
    )

async def questionnaires_keyboard(
        target_id: int, monitoring: bool = False
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=5)
    like = InlineKeyboardButton(
        text="❤️", callback_data=action_keyboard.new(action="like", target_id=target_id)
    )
    dislike = InlineKeyboardButton(
        text="👎",
        callback_data=action_keyboard.new(action="dislike", target_id=target_id),
    )
    report = InlineKeyboardButton(
        text="🔞",
        callback_data=action_keyboard.new(action="report", target_id=target_id),
    )
    go_back = InlineKeyboardButton(
        text=("💤 Berhenti"),
        callback_data=action_keyboard.new(action="stopped", target_id=target_id),
    )
    ban = InlineKeyboardButton(
        text=("🚫 Ban"),
        callback_data=action_keyboard_monitoring.new(action="ban", target_id=target_id),
    )
    next_btn = InlineKeyboardButton(
        text=("Berikutnya"),
        callback_data=action_keyboard_monitoring.new(
            action="next", target_id=target_id
        ),
    )
    if not monitoring:
        markup.row(like, report, dislike)
        markup.add(go_back)
        return markup
    else:
        markup.row(ban)
        markup.row(next_btn)
        return markup


async def reciprocity_keyboard(user_for_like: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    like = InlineKeyboardButton(
        text="❤️",
        callback_data=action_reciprocity_keyboard.new(
            action="like_reciprocity", user_for_like=user_for_like
        ),
    )
    dislike = InlineKeyboardButton(
        text="👎",
        callback_data=action_reciprocity_keyboard.new(
            action="dislike_reciprocity", user_for_like=user_for_like
        ),
    )
    markup.row(like, dislike)

    return markup


async def viewing_ques_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    view_ques = InlineKeyboardButton(text=("🚀 Lihat"), callback_data="find_ques")
    markup.row(view_ques)
    return markup


async def user_link_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    open_chat = InlineKeyboardButton(
        text=("👉 Pergi ke obrolan"), url=f"tg://user?id={telegram_id}"
    )
    report = InlineKeyboardButton(
        text="🔞 Report",
        callback_data=action_keyboard.new(action="report", target_id=telegram_id),
    )
    back = InlineKeyboardButton(
        text=("⏪️ Kembali ke melihat profil"),
        callback_data="go_back_to_viewing_ques",
    )
    markup.add(open_chat, report, back)
    return markup


async def report_menu_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    adults_only = InlineKeyboardButton(
        text="🔞 otak mesum",
        callback_data=action_report_keyboard.new(
            action="adults_only", target_id=telegram_id
        ),
    )
    drugs = InlineKeyboardButton(
        text="💊 pengedar narkoba",
        callback_data=action_report_keyboard.new(action="drugs", target_id=telegram_id),
    )
    scam = InlineKeyboardButton(
        text="💰 penipuan",
        callback_data=action_report_keyboard.new(action="scam", target_id=telegram_id),
    )
    another = InlineKeyboardButton(
        text="🦨 lain-lain",
        callback_data=action_report_keyboard.new(
            action="another", target_id=telegram_id
        ),
    )
    cancel = InlineKeyboardButton(
        text="❌ batal",
        callback_data=action_report_keyboard.new(
            action="cancel_report", target_id=telegram_id
        ),
    )
    markup.add(adults_only, drugs, scam, another, cancel)
    return markup
