import datetime, requests, pytz, time
from src.config.config import token, chat_id, bd_dates
from src.console.console_messages import send_message

telegram_bot_token = token['tg']
telegram_chat_id = chat_id['tg']

def birthday(current_date=None):
    if current_date is None:
        msk_time = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
        current_date = msk_time.strftime('%m-%d')

    content = open('other_files/date_checker.txt', 'r+')

    if current_date in bd_dates and content.read() != current_date:
        content.close()

        if type(bd_dates[current_date]) is list:
            response = requests.post(
                    f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                    data={
                        "chat_id": telegram_chat_id,
                        "text": (
                            f"🎉 <b>Сегодня особенный день!</b> 🎉\n\n"
                            f"Поздравляем с Днём Рождения замечательных людей — <b>{', '.join(bd_dates[current_date])}</b>! 🥳🎂\n\n"
                            f"✨ Желаем вам счастья, крепкого здоровья и исполнения всех желаний!\n"
                            f"🚀 Пусть каждый день приносит радость, новые возможности и только приятные сюрпризы.\n"
                            f"💡 Оставайтесь такими же яркими, талантливыми и неповторимыми!\n\n"
                            f"<i>Пусть этот год станет для вас лучшим!</i> 🎊"
                        ),
                        "parse_mode": "HTML"
                    }
                )
            
        else: 
            response = requests.post(
                    f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                    data={
                        "chat_id": telegram_chat_id,
                        "text": (
                            f"🎉 <b>Сегодня особенный день!</b> 🎉\n\n"
                            f"Поздравляем с Днём Рождения замечательного человека — <b>{bd_dates[current_date]}</b>! 🥳🎂\n\n"
                            f"✨ Желаем вам счастья, крепкого здоровья и исполнения всех желаний!\n"
                            f"🚀 Пусть каждый день приносит радость, новые возможности и только приятные сюрпризы.\n"
                            f"💡 Оставайся таким же ярким, талантливым и неповторимым!\n\n"
                            f"<i>Пусть этот год станет для тебя лучшим!</i> 🎊"
                        ),
                        "parse_mode": "HTML"
                    }
                )
            
        send_message("BIRTHDAY_MODULE_RESPONSE", response.json())

        content = open('other_files/date_checker.txt', 'w')
        content.write(current_date)
        content.close()
    else: 
        content.close()

if __name__ == "__main__":
    print("Birthday module has been started!")
    while True:
        birthday()
        time.sleep(3600*24)
