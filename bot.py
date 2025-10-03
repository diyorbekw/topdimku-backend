import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import django
from asgiref.sync import sync_to_async

# Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Verification

BOT_TOKEN = "8352691243:AAFQd2eqptfda92EKeVynsrtL0lRr5B_UmY"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Telefon yuborish uchun keyboard
request_phone_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    """
    /start <token> kelganda Verification tokenini tekshiradi
    """
    args = message.text.split()
    if len(args) == 2:
        token = args[1]
        try:
            verification = await sync_to_async(Verification.objects.get)(token=token, is_used=False)

            if not verification.is_valid():
                await message.answer("⏰ Ushbu havola eskirgan yoki ishlatilgan.")
                return

            # chat_id saqlash
            verification.chat_id = message.chat.id
            await sync_to_async(verification.save)()

            await message.answer(
                "Assalomu alaykum! Iltimos, telefon raqamingizni yuboring.",
                reply_markup=request_phone_kb
            )
        except Verification.DoesNotExist:
            await message.answer("❌ Noto‘g‘ri havola.")
    else:
        await message.answer("Botdan foydalanish uchun sayt orqali ro‘yxatdan o‘ting.")


@dp.message(F.contact)
async def phone_handler(message: types.Message):
    """
    Foydalanuvchi telefonini yuborganda tekshiradi
    """
    phone = message.contact.phone_number
    chat_id = message.chat.id

    # Telefon raqamini normalize qilish (+998...)
    if not phone.startswith("+"):
        phone = "+" + phone

    verification = await sync_to_async(
        lambda: Verification.objects.filter(chat_id=chat_id, is_used=False).order_by("-created_at").first()
    )()

    if not verification:
        await message.answer("❌ Siz uchun tasdiqlash so‘rovi topilmadi.")
        return

    if verification.phone_number != phone:
        await message.answer("❌ Telefon raqam mos kelmadi.")
        return

    await message.answer(
        f"✅ Tasdiqlash kodingiz: <b>{verification.code}</b>\n\n"
        "Iltimos, uni saytga kiriting.",
        parse_mode="HTML"
    )


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
