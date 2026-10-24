from google import genai

client = genai.Client(api_key="AQ.Ab8RN6Km9yX1icQouGJqVnC3L2vz9W-odsSL40OhOQgSE1-qUA")

interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="Explain how AI works in a few words"
)
print(interaction.output_text)