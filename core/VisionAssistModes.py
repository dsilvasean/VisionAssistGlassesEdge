import asyncio

async def intent_scene_description(assist):
    await assist.TTS.speak("Describing the scene")
    await assist.imageProcessor.setup()
    await assist.api.start_websocket()

    async def send_loop():
        while True:
            jpeg_data = await assist.imageProcessor._capture()
            print("about to emit event ")
            await assist.api.ws.emit("message", jpeg_data)
            print("emitted")
            await asyncio.sleep(assist.config.get("ImageProcessor").get("CAPTURE_EVERY")) 

    send_task = asyncio.create_task(send_loop())

    try:
        while True:
            description = await assist.ImageProcessor_queue.get()
            print(description)
            await assist.TTS.speak(description[2])

    except asyncio.CancelledError:
        print("intent_scene_description cancelled")
        send_task.cancel()
        await send_task
        raise


async def intent_ask_general_question(assist):
    await assist.TTS.speak("Genral question was asked")

