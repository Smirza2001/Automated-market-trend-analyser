from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from supporting_functions import search_tool, wiki_tool, save_tool
import gradio as gr
from fpdf import FPDF
from datetime import datetime

load_dotenv()

class MarketTrendResponse(BaseModel):
    topic: str
    trend_summary: str
    key_drivers: list[str]
    market_impact: str
    statistics: list[str]
    sources: list[str]
    tools_used: list[str]
    market_gaps: list[str] = Field(default_factory=list)
    target_segments: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

llm = ChatOpenAI(model="gpt-5.4")
parser = PydanticOutputParser(pydantic_object=MarketTrendResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an automated market trend analyser. 
Answer the input and user query: use the necessary tools and return a detailed, professional market trend report. Include a strong executive summary, clear key drivers, market impact, commercial relevance, useful supporting statistics and reliable sources. 
Adapt the report to the query: include market gaps and opportunity areas when the user asks about gaps. Include target segments and relevant demographics when the user asks about segmentation. Include proffesional recommendations when the user asks about business actions. 
Use this format for the final response and do not include anything outside it{format_instructions}
"""
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, wiki_tool, save_tool]

agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)


def export_pdf(report):
    filename = f"market_trend_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(0, 10, "Automated Market Trend Report")
    pdf.ln(4)
    pdf.set_font("Arial", "", 11)

    text = report.replace("## ", "").encode("latin-1", "replace").decode("latin-1")
    pdf.multi_cell(0, 8, text)
    pdf.output(filename)

    return filename


def generate_report(query):
    raw_response = None

    try:
        raw_response = agent_executor.invoke({"query": query})
        output_text = raw_response.get("output")

        if isinstance(output_text, list):
            output_text = output_text[0]["text"]

        structured_response = parser.parse(output_text)

        report = (
            f"## Topic\n{structured_response.topic}\n\n"
            f"## Executive Summary\n{structured_response.trend_summary}\n\n"
            f"## Relevant Stats\n" + "\n".join(f"- {item}" for item in structured_response.statistics) +
            f"\n\n## Key Drivers\n" + "\n".join(f"- {item}" for item in structured_response.key_drivers) +
            f"\n\n## Market Impact\n{structured_response.market_impact}"
            
        )

        for title, items in [
            ("Market Gaps", structured_response.market_gaps),
            ("Target Segments", structured_response.target_segments),
            ("Recommendations", structured_response.recommendations),
        ]:
            if items:
                report += f"\n\n## {title}\n" + "\n".join(f"- {item}" for item in items)

        report += (
              f"\n\n## Sources\n" + "\n".join(f"- {item}" for item in structured_response.sources) +
               f"\n\n## Tools Used\n" + "\n".join(f"- {item}" for item in structured_response.tools_used)
        )

        return report, export_pdf(report)

    except Exception as e:
        return f"## Error\n{e}\n\n```text\n{raw_response}\n```", None

with gr.Blocks(title="Automated Market Trend Analyser", fill_width=False) as demo:
    gr.Markdown("<h1 style='text-align:center;'>Automated Market Trend Analyser</h1>")
    gr.Markdown("<p style='text-align:center;'>Enter a topic to generate a market trend report.</p>")

    query = gr.Textbox(
        label="Which market trends would you like me to analyse?",
        placeholder="e.g. Market trends in ecommerce for 2026",
        lines=2
    )

    output = gr.Markdown()
    pdf_file = gr.File(label="Download PDF")

    gr.Button("Generate Report").click(generate_report, inputs=query, outputs=[output, pdf_file])

if __name__ == "__main__":
    demo.launch(inbrowser=True)