import asyncio
from VisionAssist import VisionAssist

if __name__ == "__main__":
    try:
        assist = VisionAssist()
        asyncio.run(assist.run())
    except KeyboardInterrupt:
        print("Program interrupted by user, exiting...")