from aiogram.types import (
    Message,
)

from utils.db_api import (
    db_commands,
)


async def get_statistics(message: Message):
    user = await db_commands.select_user(telegram_id=message.from_user.id)
    user_city = user.city
    users_gender_m = await db_commands.count_all_users_kwarg(sex="male")
    users_gender_f = await db_commands.count_all_users_kwarg(sex="female")
    users_city = await db_commands.count_all_users_kwarg(city=user_city)
    users_status = await db_commands.count_all_users_kwarg(status=True)
    users_verified = await db_commands.count_all_users_kwarg(verification=True)
    count_users = await db_commands.count_users()
    text = (
        "<b>📊 Statistik: </b>\n\n"
        "└Sekarang di bot kita <b>{count_users} pengguna</b>\n"
        "└Dari jumlah tersebut:\n"
        "        ├<b>{users_gender_m} pengguna pria</b>\n"
        "        ├<b>{users_gender_f} pengguna wanita</b>\n"
        "        ├<b>{users_city} pengguna dari kota {user_city}</b>\n"
        "        ├<b>{cs_uy} pengguna dari kota lain</b>\n"
        "        ├<b>{users_verified} pengguna terverifikasi</b>\n"
        "        ├<b>{users_status} pengguna yang membuat profil</b>\n"
        "└Tanggal pembuatan bot - <b>16.09.2024</b>"
    ).format(
        count_users=count_users,
        users_gender_m=users_gender_m,
        users_gender_f=users_gender_f,
        users_city=users_city,
        user_city=user_city,
        cs_uy=count_users - users_city,
        users_verified=users_verified,
        users_status=users_status,
    )
    return text
