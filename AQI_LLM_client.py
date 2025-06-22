import asyncio
from fastmcp import Client

class AQIAgent:
    def __init__(self, aqi_server_url: str, llm_server_url: str):
        self.aqi_server_url = aqi_server_url
        self.llm_server_url = llm_server_url

    async def get_aqi_report(self, location: str) -> str:
        """Call AQI MCP server tool to get AQI report."""
        async with Client(f"{self.aqi_server_url}/sse") as client:
            result = await client.call_tool("get_aqi", {"location": location})
            return self._extract_text(result)

    async def get_health_recommendations(self, aqi_report: str) -> str:
        """Call LLM MCP server tool to get health guidance."""
        async with Client(f"{self.llm_server_url}/sse") as client:
            result = await client.call_tool("suggest_aqi_actions", {"aqi_report": aqi_report})
            return self._extract_text(result)

    def _extract_text(self, result) -> str:
        """Helper to extract plain text from MCP result (list or single object)."""
        if isinstance(result, list):
            return "\n".join(block.text for block in result if hasattr(block, "text"))
        elif hasattr(result, "text"):
            return result.text
        return str(result)

async def main():
    agent = AQIAgent("http://localhost:8003", "http://localhost:8004")

    while True:
        location = input("\n📍 Enter location to check AQI (or 'exit' to quit): ").strip()
        if location.lower() == "exit":
            print("👋 Exiting AQI Assistant.")
            break

        print("\n🌫️ Fetching AQI data...")
        try:
            aqi_report = await agent.get_aqi_report(location)
            print(f"\n📊 AQI Report for '{location}':\n{aqi_report}")

            print("\n💡 Getting health precautions...")
            recommendations = await agent.get_health_recommendations(aqi_report)
            print("\n✅ Health & Safety Advice:\n", recommendations)
        except Exception as e:
            print("❌ An error occurred:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
