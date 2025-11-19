
import gradio as gr
import pandas as pd
import plotly.express as px
import json
import re
from groq import Groq

# ------------------- GROQ CLIENT -------------------
client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")  # <-- Replace safely

# ------------------- AI FUNCTION -------------------
def analyze_mood(text):
    try:
        prompt = f"""
        You are a Mood Analysis AI. Return ONLY valid JSON.

        Analyze the following text:

        \"\"\"{text}\"\"\"

        Output JSON:
        {{
            "mood": "happy/sad/angry/anxious/neutral",
            "confidence": 0-100,
            "explanation": "short explanation"
        }}
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        result_text = response.choices[0].message.content

        # Extract JSON
        json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"mood": "Unknown", "confidence": 0, "explanation": "Invalid JSON output"}

        # Clean confidence
        try:
            result["confidence"] = float(re.findall(r"\d+\.?\d*", str(result["confidence"]))[0])
        except:
            result["confidence"] = 0

        # Create bar chart
        df = pd.DataFrame({"Mood": [result["mood"]], "Confidence": [result["confidence"]]})
        fig = px.bar(df, x="Mood", y="Confidence", color="Mood", range_y=[0, 100],
                     title="Mood Confidence Level")

        return result["mood"], result["confidence"], result["explanation"], fig

    except Exception as e:
        df = pd.DataFrame({"Mood": ["Error"], "Confidence": [0]})
        fig = px.bar(df, x="Mood", y="Confidence", range_y=[0, 100], title="Error")
        return "Error", 0, str(e), fig

# ------------------- GRADIO UI -------------------
def start_app():
    with gr.Blocks() as demo:
        gr.Markdown("<h1 style='text-align: center;'>AI Mood Analyzer (GROQ)</h1>")
        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(label="Enter your text here", placeholder="Type something...", lines=5)
                analyze_btn = gr.Button("Analyze Mood")
            with gr.Column():
                mood_output = gr.Textbox(label="Detected Mood")
                confidence_output = gr.Textbox(label="Confidence (%)")
                explanation_output = gr.Textbox(label="Explanation", lines=3)
                chart_output = gr.Plot(label="Mood Confidence Chart")

        analyze_btn.click(
            analyze_mood,
            inputs=text_input,
            outputs=[mood_output, confidence_output, explanation_output, chart_output]
        )

    demo.launch()

if __name__ == "__main__":
    start_app()
