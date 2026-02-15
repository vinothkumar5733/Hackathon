!pip install reportlab

import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import styles
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os



def analyze_pitch(text):

    try:
        if not text or len(text.strip()) < 50:
            return 0,0,0,0,0,None,None,"⚠ Please enter at least 50 characters.", None

        word_count = len(text.split())


        clarity = min(100, 50 + word_count // 5)
        impact = min(100, 40 + text.count("!")*5 + word_count // 6)
        logic = min(100, 45 + word_count // 7)
        innovation = min(100, 40 + text.lower().count("ai")*10)
        market = min(100, 50 + text.lower().count("market")*8)

        overall = round(
            clarity*0.25 +
            impact*0.25 +
            logic*0.2 +
            innovation*0.15 +
            market*0.15
        ,2)


        strengths = []
        weaknesses = []
        suggestions = []

        if clarity > 70:
            strengths.append("Clear explanation of idea.")
        else:
            weaknesses.append("Pitch clarity needs improvement.")
            suggestions.append("Simplify sentences and avoid jargon.")

        if impact > 70:
            strengths.append("Strong persuasive tone.")
        else:
            weaknesses.append("Lacks emotional or persuasive impact.")
            suggestions.append("Highlight strong problem and solution impact.")

        if innovation > 70:
            strengths.append("Innovative concept.")
        else:
            suggestions.append("Emphasize uniqueness and differentiation.")

        report_text = f"""
Word Count: {word_count}

Overall Score: {overall}

Strengths:
- {"\n- ".join(strengths) if strengths else "Needs development"}

Weaknesses:
- {"\n- ".join(weaknesses) if weaknesses else "Minor weaknesses"}

Suggestions:
- {"\n- ".join(suggestions) if suggestions else "Great job! Ready for investors."}
"""



        categories = ["Clarity","Impact","Logic","Innovation","Market"]
        scores = [clarity, impact, logic, innovation, market]

        plt.figure()
        plt.bar(categories, scores)
        plt.ylim(0,100)
        plt.title("Pitch Score Breakdown")
        bar_path = "bar_chart.png"
        plt.savefig(bar_path)
        plt.close()



        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        scores_loop = scores + [scores[0]]
        angles += angles[:1]

        fig = plt.figure()
        ax = fig.add_subplot(111, polar=True)
        ax.plot(angles, scores_loop)
        ax.fill(angles, scores_loop, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0,100)

        radar_path = "radar_chart.png"
        plt.savefig(radar_path)
        plt.close()



        pdf_path = "Pitch_Report.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        elements = []

        styles_obj = styles.getSampleStyleSheet()
        elements.append(Paragraph("<b>AI Pitch Evaluation Report</b>", styles_obj["Title"]))
        elements.append(Spacer(1,0.5*inch))
        elements.append(Paragraph(f"Date: {datetime.now()}", styles_obj["Normal"]))
        elements.append(Spacer(1,0.5*inch))

        data = [
            ["Metric","Score"],
            ["Clarity", clarity],
            ["Impact", impact],
            ["Logic", logic],
            ["Innovation", innovation],
            ["Market Potential", market],
            ["Overall", overall]
        ]

        table = Table(data)
        table.setStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.grey),
            ('GRID',(0,0),(-1,-1),1,colors.black)
        ])

        elements.append(table)
        elements.append(Spacer(1,0.5*inch))
        elements.append(Paragraph(report_text.replace("\n","<br/>"), styles_obj["Normal"]))

        doc.build(elements)

        return overall, clarity, impact, logic, innovation, bar_path, radar_path, report_text, pdf_path

    except Exception as e:
        return 0,0,0,0,0,None,None,f"Error occurred: {str(e)}", None


def reset_all():
    return "",0,0,0,0,0,None,None,"",None




with gr.Blocks(theme=gr.themes.Soft()) as demo:

    gr.Markdown("# 🚀 AI Pitch Evaluation System")
    gr.Markdown("AI-powered professional startup pitch analysis")

    script_input = gr.Textbox(
        label="Enter Your Pitch",
        lines=10,
        placeholder="Paste your startup pitch here..."
    )

    gr.Examples(
        examples=[
            ["We are building an AI-powered healthcare assistant that reduces hospital workload by 40% and improves patient monitoring accuracy."],
            ["A fintech startup enabling rural businesses to access microloans using AI credit scoring."]
        ],
        inputs=script_input
    )

    analyze_btn = gr.Button("Analyze", variant="primary")
    reset_btn = gr.Button("Reset")

    gr.Markdown("## Scores")

    overall_score = gr.Number(label="Overall")
    clarity_score = gr.Number(label="Clarity")
    impact_score = gr.Number(label="Impact")
    logic_score = gr.Number(label="Logic")
    innovation_score = gr.Number(label="Innovation")

    gr.Markdown("## Visual Analysis")

    bar_chart = gr.Image(label="Bar Chart")
    radar_chart = gr.Image(label="Radar Chart")

    analysis_output = gr.Textbox(label="Detailed Report", lines=12)
    report_file = gr.File(label="Download PDF Report")

    analyze_btn.click(
        analyze_pitch,
        script_input,
        [overall_score, clarity_score, impact_score,
         logic_score, innovation_score,
         bar_chart, radar_chart,
         analysis_output, report_file]
    )

    reset_btn.click(
        reset_all,
        outputs=[script_input, overall_score, clarity_score,
                 impact_score, logic_score,
                 innovation_score,
                 bar_chart, radar_chart,
                 analysis_output, report_file]
    )

demo.launch()
