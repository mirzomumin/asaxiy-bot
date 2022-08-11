from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# from telegram.ext.ContextTypes.params import context
from telegram import ParseMode, Bot
from telegram_bot_pagination import InlineKeyboardPaginator
import requests
import bs4
import os


PORT = int(os.environ.get('PORT', 8443))
TOKEN = '5377910834:AAGE7hps1270kUgNFM07cQK00q7eFNpdtOk'



def start(update, context):
		username = update.message.from_user.first_name
		update.message.reply_html(f'Hello, {username}. I\'m ASAXIY BOT 🤖.\n\
		\nType me in what you want to find out. For example "Телефон".')


def get_info(update, context):
	text = update.message.text
	url = f'https://asaxiy.uz/product?key={text}'
	response = requests.get(url)

	soup = bs4.BeautifulSoup(response.text, 'html.parser')
	product_rows = soup.select('div.col-6.col-xl-3.col-md-4')
	if not product_rows:
		update.message.reply_html(f'Sorry, I could not find this item.\n\
			\nPlease type correct or full name of item.')
	return product_rows


def extract_info(update, context):
	product_rows = get_info(update, context)
	data = []
	for page, product_row in enumerate(product_rows):
		product = {}
		if type(product_row) == bs4.element.Tag:
			product_image = product_row.select('div.product__item-img img')[0]['data-src']
			if product_image[-5:] == '.webp':
				product_image = product_image[:-5]
				product_info_link = product_row.select('div.product__item-info > a')[0]['href']
				product_info_text = product_row.select('div.product__item-info > a > h5')[0].text
				product_price = product_row.select('span.product__item-price')[0].text
				product['image'] = product_image
				product['link'] = product_info_link
				product['text'] = product_info_text
				product['price'] = product_price
				data.append(product)
	return data


def send_info(update, context, page=1):
	data = extract_info(update, context)
	for data_element in data:
		try:
			update.message.reply_photo(
				data_element["image"],
				caption=f'{data_element["text"]}\n\
				\n{data_element["price"]}\n\
				\n<a href="asaxiy.uz{data_element["link"]}">Перейти к продукту</a>',
				parse_mode=ParseMode.HTML,)
				# reply_markup=paginator.markup,
		except:
			pass


def main():
	updater = Updater(TOKEN, use_context=True)
	dp = updater.dispatcher

	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(MessageHandler(Filters.text & (~Filters.command), send_info))

	updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
	updater.bot.setWebhook('https://bot-asaxiy.herokuapp.com/' + TOKEN)
	updater.idle()


if __name__ == "__main__":
    main()