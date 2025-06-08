from gpiozero import DistanceSensor
from picamera2 import Picamera2
import cv2
import asyncio



class ImageProcssingManager:
    def __init__(self, config):
        self.config = config.get("ImageProcessor")

        self.sensor1 = DistanceSensor(echo=self.config.get("US_SENSOR_1").get("ECHO"), trigger=self.config.get("US_SENSOR_1").get("TRIGGER"), max_distance=self.config.get("US_SENSOR_1").get("MAX_DISTANCE"))
        self.sensor2 = DistanceSensor(echo=self.config.get("US_SENSOR_2").get("ECHO"), trigger=self.config.get("US_SENSOR_2").get("TRIGGER"), max_distance=self.config.get("US_SENSOR_2").get("MAX_DISTANCE"))

        # self.picam2 = Picamera2()
        # if self.config.get("PI_CAMERA").get("CONFIG_TYPE" == "STILL"):
        #     capture_config = self.picam2.create_still_configuration(main={"size": (self.config.get("PI_CAMERA").get("SIZE").get("X"),self.config.get("PI_CAMERA").get("SIZE").get("Y"))})
        #     self.picam2.configure(capture_config)
        #     self.picam2.start()
    
    def _capture_sync(self,):
        np_array = self.picam2.capture_array()
        _, jpeg_data = cv2.imencode(".jpg", np_array, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        print(jpeg_data)
        return jpeg_data
    
    async def _capture(self):
        print("hey i was called")
        loop = asyncio.get_running_loop()
        jpeg_data = await loop.run_in_executor(None, self._capture_sync)
        print(jpeg_data)
        return jpeg_data
    
    async def setup(self):
        self.picam2 = Picamera2()
        if self.config.get("PI_CAMERA").get("CONFIG_TYPE") == "STILL": 
            capture_config = self.picam2.create_still_configuration(main={"size": (self.config.get("PI_CAMERA").get("SIZE").get("X"),self.config.get("PI_CAMERA").get("SIZE").get("Y"))})
            self.picam2.configure(capture_config)
            self.picam2.start()
            print("SETUP COMPLETED")




