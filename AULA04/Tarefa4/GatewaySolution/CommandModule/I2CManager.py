from threading import Thread
import smbus2
import time
#import array

class I2CManager:
	def __init__(self, busNumber, address, ackEvent, mvEvent, stopEvent):

		self.bus = None
		self.busNumber = busNumber
		self.address = address
		self.stopped = False

		# self.lastData = ""
		# self.ack = False
		self.error = False
		# self.lastAck = time.time()

		self.ackEvent = ackEvent
		self.mvEvent = mvEvent
		self.stopEvent = stopEvent

		print("Starting Serial BUS {} at {}".format(self.busNumber, self.address))

		if self.bus == None:
			self.bus = smbus2.SMBus(self.busNumber)
			time.sleep(1)
		
		print("Serial BUS started!")

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	# def isBusy(self):
	# 	return not self.ack

	def update(self):


		while True:
			if self.stopped:
				return
				
			try:
				# Read a block of 16 bytes from address ADDRESS, offset 0
				data = bytes(self.bus.read_i2c_block_data(self.address, 0, 16)).decode('cp855').rstrip()

				if len(data) > 1:
					#print("Processing incoming {} bytes ... {}".format(len(data), data))

					if data.find("ACK") > -1:
						self.ackEvent()

					elif data.find("MV") > -1:

						deltaT = float ( data[2:5] ) #in seconds
						omegaL = int ( data[5:8] ) #in RPM
						omegaR = int ( data[8:] ) #in RPM

						self.mvEvent(deltaT,omegaL,omegaR)

					elif data.find("ST") > -1:

						self.stopEvent()

					else:
						print("Unknown message: "+data)


				
				# else:
				# 	print("Serial BUS is empty")
				self.error = False

			except Exception as e:

				print("I2C Manager communication error on receiving %s " % e)

				self.error = True
				time.sleep(1)

				self.bus = None
				self.stopped = False
				self.lastData = ""
				#self.ack = False

				print("Starting Serial BUS {} at {}".format(self.busNumber, self.address))

				if self.bus == None:
					self.bus = smbus2.SMBus(self.busNumber)
					time.sleep(1)
				
				print("Serial BUS started!")

			time.sleep(0.5)


	# def read(self):
	# 	r = self.lastData
	# 	self.lastData = ""
	# 	return r

	def send(self, command):

		try:
			if self.bus != None:
				#print("Sending command to I2C BUS: {}".format(command))
				#self.lastData = ""
				self.bus.write_i2c_block_data(self.address, 0, command.encode('utf-8'))			
			else:
				print("Serial not ready!")
			self.error = False
		except Exception as e:

			print("I2C Manager communication error on sending %s " % e)
			self.error = True

			time.sleep(1)

			self.bus = None
			self.stopped = False
			# self.lastData = ""
			# self.ack = False

			print("Starting Serial BUS {} at {}".format(self.busNumber, self.address))

			if self.bus == None:
				self.bus = smbus2.SMBus(self.busNumber)
				time.sleep(1)
			
			print("Serial BUS started!")

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True        

