import asyncio
from fastmcp.client import Client

class AQIAgent:
    def __init__(self, aqi_server_url: str = "http://localhost:8003"):
        self.aqi_server_url = aqi_server_url

    async def get_aqi(self, location: str) -> str:
        async with Client(f"{self.aqi_server_url}/sse") as client:
            result = await client.call_tool("get_aqi", {"location": location})

            # ✅ Handle content block list
            if isinstance(result, list) and hasattr(result[0], "text"):
                return "\n".join(block.text for block in result if hasattr(block, "text"))

            # ✅ If it's just a single content block
            if hasattr(result, "text"):
                return result.text

            # ✅ Fallback
            return str(result)

async def main():
    agent = AQIAgent()

    while True:
        location = input("🌍 Enter a location to get AQI (or type 'exit' to quit): ").strip()
        if location.lower() == "exit":
            print("👋 Exiting AQI Client.")
            break

        print("\n🔍 Fetching air quality data...")
        try:
            aqi_report = await agent.get_aqi(location)
            print(f"\n📄 AQI Report for '{location}':\n{aqi_report}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
