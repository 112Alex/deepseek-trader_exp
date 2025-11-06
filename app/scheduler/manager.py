from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.scheduler.jobs import check_signals_and_notify

def setup_scheduler(bot):
	"""
	Инициализирует и запускает планировщик APScheduler для рассылки сигналов.
	"""
	scheduler = AsyncIOScheduler()
	# Добавляем задачу: рассылка сигналов каждую минуту
	scheduler.add_job(check_signals_and_notify, 'interval', minutes=1, args=[bot], id='signal_notifier')
	scheduler.start()
	return scheduler
