import sys
import os
import datetime
import calendar
import zipfile
import telebot
from time import sleep
from apscheduler.schedulers.blocking import BlockingScheduler
from csv_generator import generateCSV



def retrieve_media():
    TOKEN = 'AQUI TIENE QUE IR EL TOKEN DEL BOT'
    tb = telebot.TeleBot(TOKEN)
    AppID     = 'ID DEL APP DE FACEBOOK'
    AppSecret = 'SECRET ID DEL APP DE FACEBOOK'
    dicMedios = \
        {
            'Amelia Rueda'  : '142921462922',
            'CRHoy'         : '265769886798719',
            'Extra'         : '109396282421232',
            'Financiero'    : '47921680333',
            'Monumental'    : '111416968911423',
            'Nacion'        : '115872105050',
            'Prensa Libre'  : '228302277255192',
            'Repretel'      : '100237323349361',
            'Semanario'     : '119189668150973',
            'Telenoticias'  : '116842558326954'
        }

    retrieve_date = datetime.date.today()
    retrieve_month = retrieve_date.month
    retrieve_day = retrieve_date.day
    retrieve_year = retrieve_date.year

    # rango para cuando es día 2 y el mes anterior es de 30 días
    if retrieve_day == 2  and (retrieve_month == 5 or retrieve_month == 7 or retrieve_month == 10 or retrieve_month == 12) :
        sinceDate = retrieve_date - datetime.timedelta(days=5)
        print('30 dias')
    # rango para cuando febrero (mes de 28 días)
    elif retrieve_day == 2  and retrieve_month == 3:
        sinceDate = retrieve_date - datetime.timedelta(days=3)
        print('febrero normal')
    # rango para cuando febrero es bisiesto (mes de 29 días)
    elif calendar.isleap(retrieve_year) and retrieve_day == 2  and retrieve_month == 3:
        sinceDate = retrieve_date - datetime.timedelta(days=4)
        print('febrero bisiesto')
    # rango para cuando es día 7 del mes o es día 2 y el mes anterior fue de 31 días
    else :
        sinceDate = retrieve_date - datetime.timedelta(days=6)
        print('31 dias')


    untilDate = retrieve_date - datetime.timedelta(days=2)
    sinceDate_formated = sinceDate.strftime("%Y-%m-%d %H:%M:%S")
    untilDate_formated = untilDate.strftime("%Y-%m-%d %H:%M:%S")
    untilDate_formated = untilDate_formated.replace('00:00:00', '23:59:59')

    # esto se tiene que cambiar por la conexion con la base
    # TO-DO: excepcion para La Nacion
    # Genera los CSV de cada medio y los guarda en archivos zip
    for mediaName, mediaId in dicMedios.items():
        generateCSV(AppID, AppSecret, mediaName, mediaId, sinceDate_formated, untilDate_formated)

    # Esta sección crea un zip para almacenar todos los zips de todos los medios
    # Quita la hora de las fechas para que el nombre del archivo final sea más legible
    since_file = sinceDate_formated.replace(' 00:00:00', '')
    until_file = untilDate_formated.replace(' 23:59:59', '')

    # Se crea un archivo Media con el rango de las fechas
    media_zipped = zipfile.ZipFile('Media_'+since_file+'-'+until_file+'.zip', mode='w')
    media_file_zipped = 'Media_'+since_file+'-'+until_file+'.zip'
    try:
        # Guarda cada uno de los zips de cada medio en el zip Media
        for mediaName, mediaId in dicMedios.items():
            media_zipped.write(mediaName+'_'+since_file+'-'+until_file+'.zip')
    finally:
        #Cierra el archivo Media y borra los zip de cada medio
        media_zipped.close()
        for mediaName, mediaId in dicMedios.items():
            os.remove(mediaName+'_'+since_file+'-'+until_file+'.zip')
    doc = open('Media_'+since_file+'-'+until_file+'.zip', 'rb')
    tb.send_document('-229323512', doc, timeout=40)

    return media_file_zipped

sched = BlockingScheduler()
sched.add_job(retrieve_media, 'cron', day='7,12,17,22,27,2', hour=20, minute=0)

#@sched.scheduled_job('interval', seconds=10)
#def timed_job():
#    print('This job is run every 10 seconds.')

#@sched.scheduled_job('cron', day_of_week='mon-fri', hour=10)
#def scheduled_job():
#    print('This job is run every weekday at 10am.')

#sched.configure(options_from_ini_file)
sched.start()

def sendMedia(bot, update, since_file, until_file):
    bot.send_document(chat_id='-229307484',
                      document=open('Media_' + since_file + '-' + until_file + '.zip', 'rb'),
                      timeout=300*60)