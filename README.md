# Automated Market Trend Analyser

A browser-based market research and reporting tool that turns a user query into a structured trend/insight report.

By exploring a range of langChain workflow resources/tutorials as initial reference points. I was able to derive a strong structural foundation for this platform. From there, it was adapted intentionally into a more business-focused market trend analysis tool. The most recent version was shaped around a different use case and a more structured reporting format. Additionally, Gradio was added to provide a simple browser interface. Furthermore, PDF export was included to make the output easier to save and share.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

Before running: create `.env` file and add your own API key

```env
OPENAI_API_KEY=INSERT_YOUR_OWN_KEY_HERE
```
