import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import Router

API_TOKEN = "8205255739:AAHz5r22gc5A23uROMbwej5QbiyHC4umgf0"

# Admin ID lar ro‘yxati
ADMIN_IDS = [8454801295, 7781534875]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

qa_dict = {}
mode_dict = {}  # adminning holatini saqlash uchun

# Adminni tekshiruvchi yordamchi funksiya
async def is_admin(message: types.Message) -> bool:
    return message.from_user.id in ADMIN_IDS

# /start komandasi tugma bilan
@router.message(Command("start"))
async def start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Bizning kanal", url="https://t.me/MyChannel")
            ],
            [
                types.InlineKeyboardButton(text="Savol qo‘shish", callback_data="add_question")
            ],
            [
                types.InlineKeyboardButton(text="Tayyor savol-javob", callback_data="ready_qa")
            ]
        ]
    )
    await message.answer("Salom! 👋 Tugmalardan birini tanlang:", reply_markup=keyboard)

# Callback tugmalarni ushlash
@router.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    if callback.data == "add_question":
        if callback.from_user.id in ADMIN_IDS:
            mode_dict[callback.from_user.id] = "waiting_question"
            await callback.message.answer("✍️ Savolni kiriting:")
        else:
            await callback.message.answer("❌ Siz admin emassiz, savol qo‘sha olmaysiz.")
    elif callback.data == "ready_qa":
        if qa_dict:
            text = "📖 Tayyor savol-javoblar:\n\n"
            for q, a in qa_dict.items():
                text += f"❓ {q}\n✅ {a}\n\n"
            await callback.message.answer(text)
        else:
            await callback.message.answer("❌ Hozircha tayyor savol-javoblar yo‘q.")
    await callback.answer()

# Admin matn yozganda savol/javobni olish
@router.message()
async def handle_text(message: types.Message):
    if not await is_admin(message):
        return  # oddiy foydalanuvchi savol/javob qo‘sha olmaydi

    state = mode_dict.get(message.from_user.id)
    if state == "waiting_question":
        qa_dict["last_question"] = message.text.strip().lower()
        mode_dict[message.from_user.id] = "waiting_answer"
        await message.reply(f"Savol qabul qilindi: {message.text}\nEndi javobni kiriting ✍️")
    elif state == "waiting_answer":
        question = qa_dict.get("last_question")
        qa_dict[question] = message.text.strip()
        mode_dict[message.from_user.id] = None
        await message.reply(f"Savol-javob saqlandi ✅\n'{question}' → '{message.text}'")

# Guruhdagi savollarga javob berish
@router.message()
async def reply_in_group(message: types.Message):
    text = message.text.lower()
    if text in qa_dict:
        await message.reply(qa_dict[text])
        await message.reply("📢 Bizning kanalga qo‘shiling: @fergo_news")

# Yangi foydalanuvchi qo‘shilganda adminlarga xabar yuborish
@router.message()
async def new_member(message: types.Message):
    if message.new_chat_members:
        for member in message.new_chat_members:
            for admin_id in ADMIN_IDS:
                await bot.send_message(admin_id, f"👤 Yangi foydalanuvchi qo‘shildi: {member.full_name}")
        await message.reply("📢 Xush kelibsiz! Bizning kanalga qo‘shiling: @fergo_news")

# Reklama komandasi
@router.message(Command("reklama"))
async def reklama(message: types.Message):
    await message.reply("📢 Bizning kanalga qo‘shiling: @fergo_news")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())