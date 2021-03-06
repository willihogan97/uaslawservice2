from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pika
import datetime
import time
import sys
import requests
import urllib.request
import datetime
import mimetypes

# Create your views here.
class FilesMethods:
	@csrf_exempt
	def startOrchestrator(request):
		newSubProcess = subprocess.Popen("./process_tasks.sh", shell=True,stdout=subprocess.PIPE, preexec_fn=os.setsid)
		FilesMethods.orchestrator(newSubProcess.pid)

	@csrf_exempt
	def orchestrator(pid):
		credentials = pika.PlainCredentials('1506725003', '697670')
		connection = pika.BlockingConnection(pika.ConnectionParameters('152.118.148.103',5672,'1506725003', credentials))
		channel = connection.channel()
		exchange = '1506725003'
		channel.exchange_declare(exchange=exchange, exchange_type='direct', passive=False, durable=False, auto_delete=False)

		result = channel.queue_declare('', exclusive=True)
		queue_name = result.method.queue
		channel.queue_bind(
		    exchange=exchange, queue=queue_name, routing_key="dataServer1")


		channel_fanout = connection.channel()
		exchange_fanout = '1506725003_fanout'
		channel_fanout.exchange_declare(exchange=exchange_fanout, exchange_type='fanout', passive=False, durable=False, auto_delete=False)

		# result_fanout = channel_fanout.queue_declare('', exclusive=True)
		# queue_name_fanout = result_fanout.method.queue
		# channel_fanout.queue_bind(
		#     exchange=exchange, queue=queue_name, routing_key="fanoutdataserver2")
		
		# channel.queue_bind(
		#     exchange=exchange, queue=queue_name, routing_key="waktuServer")

		print(' [*] Waiting for logs. To exit press CTRL+C')

		def callback(ch, method, properties, body):
			print(" [x] %r:%r" % (method.routing_key, body))
			print(body.decode("UTF-8"))
			splitBody = body.decode("UTF-8").split(";")
			counter = splitBody[0]
			urlFile = splitBody[1]
			token = splitBody[2]
			oauthValidate = FilesMethods.oauthValidate(token)
			if oauthValidate:
				filename = FilesMethods.download(urlFile)
				channel_fanout.basic_publish(exchange=exchange_fanout,
					routing_key='fanoutdataserver2',
					body="urlberhasil;" + filename)
			else:
				channel_fanout.basic_publish(exchange=exchange_fanout,
					routing_key='fanoutdataserver2',
					body="validasi_gagal")

		channel.basic_consume(
			queue=queue_name, on_message_callback=callback, auto_ack=True)

		channel.start_consuming()

	@csrf_exempt
	def oauthValidate(token):
		url = "https://oauth.infralabs.cs.ui.ac.id/oauth/resource"
		headers = {"Authorization": token}
		r = requests.get(url, headers=headers)
		if r.status_code != 401 :
			return True
		else:
			return False

	@csrf_exempt
	# def download(url, counter):
	def download(url):
		filename = url[url.rfind("/")+1:]
		print(filename)
		downloadFile = urllib.request.urlopen(url)
		# mime = mimetypes.guess_type(url, strict=True)
		# ext = ""
		# if mime != None:
		# 	ext = mimetypes.guess_extension(mime[0])
		# 	print(ext)
		# ts = datetime.datetime.today().strftime('%d %B %Y, %H:%M:%S')
		# # content_dispotition = downloadFile.getheader('Content-Dispotition')
		# # print(content_dispotition)
		# # filename = ""
		# # if content_dispotition != None;
		# filename = ts + "url" + counter + ext
		filepath = "../../files/" + filename
		# filepath = "../files/" + ts
		datatowrite = downloadFile.read()
		with open(filepath, 'wb') as f:  
		    f.write(datatowrite)
		return filename
