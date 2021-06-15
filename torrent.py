import telegram
from telegram import ChatAction, InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler,MessageHandler,Filters,CallbackQueryHandler,PicklePersistence
from telegram.ext.dispatcher import run_async
from telegram_bot_pagination import InlineKeyboardPaginator
import logging
import os
import requests
from tpblite import TPB
t = TPB()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

@run_async
def start(update,context):
	name=update.message.chat.first_name
	update.message.reply_text("Hi! "+name+"\nWelcome to Torrent Search Bot 😃,\nYou can search torrents using this bot just send me a search query to get started")

@run_async    
def search (update,context):
	try:
		history=context.user_data['history']
	except KeyError:
		history=context.user_data['history']=[]
	search_query=update.message.text
	history.append(search_query)
	context.bot.send_chat_action(chat_id=update.effective_message.chat_id ,action=telegram.ChatAction.TYPING)
	torrents = t.search(search_query)
	try:
		result=context.user_data['result']
	except KeyError:
		result = context.user_data['result'] = []
	try:
		magnet_link=context.user_data['magnet_link']
	except KeyError:
		magnet_link=context.user_data['magnet_link']=[]
	try:
		torrent_name=context.user_data['torrent_name']
	except KeyError:
		torrent_name=context.user_data['torrent_name']=[]
	i=0
	for torrent in torrents:
		name=torrent.title
		torrent_name.insert(i,(name))
		magnet=torrent.magnetlink
		magnet_link.insert(i,(magnet))
		seeder=torrent.seeds
		leechers=torrent.leeches
		upload_date=torrent.upload_date
		size=torrent.filesize
		a=i+1
		
		link="/get_magnet_link"+str(a)
		result.insert(i,(str(i+1)+") "+name+"\nsize: "+size+"\nMagnet Link: "+link+"\nSeeders: "+str(seeder)+"\nLeechers: "+str(leechers)+"\nUpload Date: "+str(upload_date)+"\n\n"))
		i+=1
	
	if len(result)%4==0:
		pass
	elif len(result)%4==1:
		result.pop()
	elif len(result)%4==2:
		result.pop()
		result.pop()
	elif len(result)%4==3:
		result.pop()
		result.pop()
		result.pop()
	
	N=4
	temp = '{} ' * N
	result = [temp.format(*ele) for ele in zip(*[iter(result)] * N)]
	context.user_data['result']=result
	paginator = InlineKeyboardPaginator(
	len(result),
    current_page=1)
	
	update.message.reply_text(text=result[0],reply_markup=paginator.markup,parse_mode=telegram.ParseMode.HTML)


@run_async        
def getlink(update,context):
	get=update.message.text
	num=get.split("link")[1]
	number=int(num)
	context.bot.send_chat_action(chat_id=update.effective_message.chat_id ,action=telegram.ChatAction.TYPING)
	magnet_link=context.user_data['magnet_link']
	torrent_name=context.user_data['torrent_name']
	link=magnet_link[number-1]
	torrent=torrent_name[number-1]
	update.message.reply_text(torrent+f"\nmagnet Link : <pre>{link}</pre>",parse_mode=telegram.ParseMode.HTML)
	
def history (update,context):
	history=context.user_data['history']
	if len(history)==0:
		update.message.reply_text("Your search history is empty")
	else:
		history="\n".join(history)
		update.message.reply_text("You have searched for the following torrents:\n"+history+"\n\nclick  /clear to clear history")
	
	
	
	
			
def clear(update,context):
	try:
		history=context.user_data['history']
		history.clear()
		update.message.reply_text("Searched history cleared")

	except:
		update.message.reply_text("Your search history is empty")
	try:
		magnet_link=context.user_data['magnet_link']
		magnet_link.clear()
	except:
		pass
	try:
		result=context.user_data['result']
		result.clear()
	except:
		pass
			
			
def button(update,context):
	result=context.user_data['result']
	query = update.callback_query
	query.answer()
	
	page = int(query.data)
	paginator = InlineKeyboardPaginator(len(result),current_page=page,data_pattern='{page}')
	query.edit_message_text(text=result[page - 1],reply_markup=paginator.markup,parse_mode=telegram.ParseMode.HTML)

persistence=PicklePersistence('torrentdata')
def main():
    token=os.environ.get("bot_token", "")
    updater = Updater(token,use_context=True, persistence=persistence)
    dp=updater.dispatcher
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('history', history))
    dp.add_handler(CommandHandler("clear",clear))
    dp.add_handler(MessageHandler(Filters.regex(r'(/get_magnet_link*)'),getlink))
    dp.add_handler(MessageHandler(Filters.text, search))
    dp.add_handler(CallbackQueryHandler (button))
    updater.start_polling()
    updater.idle()
 
	
if __name__=="__main__":
	main()




	
