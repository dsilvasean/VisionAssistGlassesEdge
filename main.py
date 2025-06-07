import asyncio
from VisionAssist import VisionAssist

if __name__ == "__main__":
    assist = VisionAssist()
    asyncio.run(assist.run())