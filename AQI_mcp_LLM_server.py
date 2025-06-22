from fastmcp import FastMCP
from transformers import pipeline

# Initialize the MCP LLM Server
mcp = FastMCP("AQI-LLM", host="0.0.0.0", port=8004)

# Load your Hugging Face text-generation pipeline
# Make sure the model is downloaded and compatible with your hardware
generator = pipeline(
    "text-generation",
    model="meta-llama/Llama-3.2-3B-Instruct",  # You can swap with mistralai/Mistral-7B-Instruct if supported
    device=0,  # Use 0 if you have GPU support, otherwise remove this argument
    max_new_tokens=512,
)

@mcp.tool()
async def suggest_aqi_actions(aqi_report: str) -> str:
    """Generate health and safety recommendations based on AQI report."""
    prompt = f"""
You are a health assistant specializing in environmental safety. Based on the Air Quality Index (AQI) report below, provide:

1. General air quality level.
2. Health hazards associated.
3. Recommended precautions.
4. Specific guidance for sensitive groups (children, elderly, those with asthma).

AQI Report:
{aqi_report}
"""

    output = generator(prompt, do_sample=True, temperature=0.7)
    result = output[0]["generated_text"]
    result = result.split("📍 Enter")[0].strip()
    return result

if __name__ == "__main__":
    mcp.run(transport="sse")
