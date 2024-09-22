from abc import (
    ABC,
    abstractmethod,
)
import asyncio
import random
import secrets

from aiogram.dispatcher import (
    FSMContext,
)
from aiogram.types import (
    CallbackQuery,
)

from data.config import (
    load_config,
)
from functions.dating.create_forms_funcs import (
    create_questionnaire,
    create_questionnaire_reciprocity,
    rand_user_list,
)
from functions.dating.get_next_user_func import (
    get_next_user,
)
from functions.main_app.auxiliary_tools import (
    get_report_reason,
)
from keyboards.inline.main_menu_inline import (
    start_keyboard,
)
from keyboards.inline.questionnaires_inline import (
    stopped_keyboard,
)
from keyboards.inline.questionnaires_inline import (
    report_menu_keyboard,
    user_link_keyboard,
)
from keyboards.default.stop import (
    stop_keyboard,
)
from loader import (
    bot,
)
from utils.db_api import (
    db_commands,
)

class ActionStrategy(ABC):
    @abstractmethod
    async def execute(
            self, call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
    ):
        pass


class StartFindingSuccess(ActionStrategy):
    async def execute(self, call: CallbackQuery, state: FSMContext, **kwargs):
        await call.message.delete()
        telegram_id = call.from_user.id
        user_list = await get_next_user(telegram_id)
        reply_markup = stop_keyboard()
        await call.message.answer("semoga mendapatkan jodoh", reply_markup=reply_markup)
        random_user = random.choice(user_list)
        await create_questionnaire(form_owner=random_user, chat_id=telegram_id)
        await state.set_state("finding")


class StartFindingFailure(ActionStrategy):
    async def execute(self, call: CallbackQuery, state: FSMContext, **kwargs):
        await call.answer("Tidak ada waktu untuk melakukan apa pun selain Anda")


class StartFindingReachLimit(ActionStrategy):
    async def execute(self, call: CallbackQuery, state: FSMContext, **kwargs):
        await call.answer(
            text=("Akun anda telah mencapai limit per hari untuk reaction profil, kembali lagi besok"), show_alert=True
        )
        info = await bot.get_me()
        await call.message.answer(
            text=(
                "Terlalu banyak ❤️ untuk hari ini.\n\n"
                "Undang teman dan dapatkan lebih banyak ❤️\n\n"
                "https://t.me/{}?start={}\n\n"
                "Atau temukan lebih banyak teman di @fwarandombot"
            ).format(info.username, call.from_user.id), reply_markup=await start_keyboard(call),
        )
        await call.message.answer(
            text=(
                "dapatkan lebih banyak ❤️\n"
                "#fwabase\n"
                "📸 tiktok.com/tag/fwabase"
            ), disable_web_page_preview=True)
        await state.reset_data()

class LikeAction(ActionStrategy):
    async def execute(
            self, call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
    ):
        user = await db_commands.select_user_object(telegram_id=call.from_user.id)
        text = ("Seseorang menyukai profil anda")
        target_id = int(callback_data["target_id"])

        await create_questionnaire(
            form_owner=call.from_user.id, chat_id=target_id, add_text=text
        )

        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=None,
        )

        await db_commands.update_user_data(
            telegram_id=call.from_user.id, limit_of_views=user.limit_of_views - 1
        )
        await create_questionnaire(
            form_owner=(await rand_user_list(call)), chat_id=call.from_user.id
        )

        await state.reset_data()


class DislikeAction(ActionStrategy):
    async def execute(
            self, call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
    ):
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=None,
        )
        await create_questionnaire(
            form_owner=(await rand_user_list(call)), chat_id=call.from_user.id
        )
        await state.reset_data()


class StoppedAction(ActionStrategy):
    async def execute(
            self, call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
    ):
        text = (
            "Senang bisa membantu, {fullname}!\nSaya harap Anda menemukan seseorang berkat saya"
        ).format(fullname=call.from_user.full_name)
        await call.answer(text, show_alert=True)
        user = await db_commands.select_user(telegram_id=call.from_user.id)
        user_verification = "✅" if user.verification else ""
        user_info_template = (
            "{name}, {age} tahun, {city}, {verification}\n\n{commentary}\n\n"
            "Filter pasangan anda:\n\n"
            "🚻 lawan jenis anda: {need_partner_sex}\n"
            "🔞 Rentang usia: {min}-{max} tahun\n\n"
            "🏙️ kota: {need_city}"
        )
        user_info = user_info_template.format(
            name=user.varname,
            age=user.age,
            city=user.city,
            verification=user_verification,
            commentary=user.commentary,
            need_partner_sex=user.need_partner_sex,
            min=user.need_partner_age_min,
            max=user.need_partner_age_max,
            need_city=user.need_city,
        )

        await call.message.answer_photo(
            caption=user_info, photo=user.photo_id,
            reply_markup=await start_keyboard(call),
        )
        await state.reset_state()


class LikeReciprocity(ActionStrategy):
    async def execute(
            self, call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
    ):
        user_for_like = int(callback_data["user_for_like"])
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=None,
        )
        useri = await db_commands.select_user(telegram_id=user_for_like)
        user = await db_commands.select_user(telegram_id=call.from_user.id)
        await call.message.delete()
        textile = ("{}, {} tahun, {}\n\n{}").format(useri.varname, useri.age, useri.city, useri.commentary)
        await call.message.answer_photo(caption=textile, photo=useri.photo_id)
        await call.message.answer(
            text=("Matching! Semoga ini jodoh anda;) Mulailah mengobrol 👉 dengan <a href='tg://user?id={}'>{}</a> ").format(useri.telegram_id, useri.varname),
            reply_markup=await user_link_keyboard(telegram_id=user_for_like),
        )
        await create_questionnaire_reciprocity(
            liker=call.from_user.id, chat_id=user_for_like, add_text=""
        )
        await bot.send_message(
            chat_id=user_for_like,
            text=("Ada rasa saling simpati! Mulai berkomunikasi👉 dengan <a href='tg://user?id={}'>{}</a> ").format(user.telegram_id, user.varname),
            reply_markup=await user_link_keyboard(telegram_id=call.from_user.id),
        )
        await state.reset_state()


class DislikeReciprocity(ActionStrategy):
    async def execute(
            self, call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
    ):
        user = await db_commands.select_user(telegram_id=call.from_user.id)
        user_verification = "✅" if user.verification else ""
        user_info_template = (
            "{name}, {age} tahun, {city}, {verification}\n\n{commentary}\n\n"
            "Filter pasangan anda:\n\n"
            "🚻 lawan jenis anda: {need_partner_sex}\n"
            "🔞 Rentang usia: {min}-{max} tahun\n\n"
            "🏙️ kota: {need_city}"
        )
        user_info = user_info_template.format(
            name=user.varname,
            age=user.age,
            city=user.city,
            verification=user_verification,
            commentary=user.commentary,
            need_partner_sex=user.need_partner_sex,
            min=user.need_partner_age_min,
            max=user.need_partner_age_max,
            need_city=user.need_city,
        )

        await call.message.answer_photo(
            caption=user_info, photo=user.photo_id,
            reply_markup=await start_keyboard(call),
        )
        await state.reset_state()


class GoBackToViewing(ActionStrategy):
    async def execute(
            self, call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
    ):
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=None,
        )

        user_list = await get_next_user(call.from_user.id)
        random_user = secrets.choice(user_list)
        await state.set_state("finding")
        try:
            await create_questionnaire(
                form_owner=random_user, chat_id=call.from_user.id
            )
            await state.reset_data()
        except IndexError:
            await call.answer("Saat ini kami tidak memiliki profil yang cocok untuk Anda, silahkan undang teman anda agar kami lebih banyak pilihan untuk anda")
            await state.reset_data()


class ChooseReportReason(ActionStrategy):
    async def execute(
            self, call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
    ):
        await state.reset_state()
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=None,
        )
        target_id = int(callback_data["target_id"])
        await call.message.answer(
            text=("<u>Pilih alasan keluhan:</u>"),
            reply_markup=await report_menu_keyboard(telegram_id=target_id),
        )


class SendReport(ActionStrategy):
    async def execute(
            self, call: CallbackQuery, state: FSMContext, callback_data: dict[str, str]
    ):
        target_id = int(callback_data["target_id"])
        target_user = await db_commands.select_user(telegram_id=target_id)

        counter_of_report = target_user.counter_of_report
        username = call.from_user.username
        user_id = call.from_user.id
        report_reason = await get_report_reason(call)

        text = (
            "Keluhan dari pengguna: <code>[@{username}</code> | <code>{tg_id}</code>]\n\n"
            "Kepada: <code>[{owner_id}]</code>\n"
            "Alasan keluhan: <code>{reason}</code>\n"
            "Jumlah keluhan dari pengguna: <code>{counter_of_report}</code>"
        ).format(
            username=username,
            tg_id=user_id,
            owner_id=target_id,
            reason=report_reason,
            counter_of_report=counter_of_report,
        )

        await db_commands.update_user_data(
            telegram_id=target_id, counter_of_report=counter_of_report + 1
        )

        moderate_chat = load_config().tg_bot.moderate_chat
        if counter_of_report >= 2 and not target_user.on_check_by_admin:
            await db_commands.update_user_data(
                telegram_id=target_id, on_check_by_admin=True
            )
            await create_questionnaire(
                form_owner=target_id,
                chat_id=moderate_chat,
                report_system=True,
                add_text=text,
            )
        await asyncio.sleep(0.5)
