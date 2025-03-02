from nicegui import ui
import matplotlib.pyplot as plt
import io
import base64

answers = ['Neutral'] * 8

questions = [
    'I prefer to learn by seeing diagrams or illustrations.',
    'I prefer to listen to explanations or lectures.',
    'I prefer to learn by doing hands-on activities.',
    'I prefer reading textbooks or written instructions over watching a video.',
    'I find it easier to understand information when I hear it spoken aloud.',
    'I learn best when I take detailed notes while studying.',
    'I find it easier to remember information when I see it written down or in charts.',
    'I understand concepts better when I can physically interact with them.',
]

styles = [
    'visual',
    'auditory',
    'kinesthetic',
    'reading/writing',
    'auditory',
    'reading/writing',
    'visual',
    'kinesthetic'
]

agreement_points = {
    'Strongly Agree': 4,
    'Agree': 3,
    'Neutral': 2,
    'Disagree': 1,
    'Strongly Disagree': 0,
}

def calculate_learning_style():
    score_visual = 0
    score_auditory = 0
    score_kinesthetic = 0
    score_readingwriting = 0

    for answer, style in zip(answers, styles):
        if style == 'visual':
            score_visual += agreement_points[answer]
        elif style == 'auditory':
            score_auditory += agreement_points[answer]
        elif style == 'kinesthetic':
            score_kinesthetic += agreement_points[answer]
        elif style == 'reading/writing':
            score_readingwriting += agreement_points[answer]
    
    # Create a dictionary to map scores to styles
    style_scores = {
        'Visual': score_visual,
        'Auditory': score_auditory,
        'Kinesthetic': score_kinesthetic,
        'Reading/Writing': score_readingwriting
    }

    return style_scores

def create_pie_chart(scores):
    labels = list(scores.keys())
    sizes = list(scores.values())

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Convert the plot to a base64-encoded string
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return image_base64

@ui.page('/', dark=True)
def survey_page():
    ui.label('How much do you agree with the following statements?').classes('text-xl')
    for i, (q, s) in enumerate(zip(questions, styles)):
        ui.label(q).props('inline').classes('text-md')
        ui.radio(options=['Strongly Agree', 'Agree', 'Neutral', 'Disagree', 'Strongly Disagree'], value='Neutral').props('inline').on_value_change(lambda e, index=i: answers.__setitem__(index, e.value))

    ui.link('Submit', results_page).classes('mt-4')

@ui.page('/results')
def results_page():
    ui.label('Thank you for submitting the survey!').classes('text-xl')
    style_scores = calculate_learning_style()
    max_learning_style = max(style_scores, key=style_scores.get)
    ui.label(f'Your learning style is {max_learning_style}!').classes('text-lg')

    # Create and display the pie chart
    chart_image = create_pie_chart(style_scores)
    ui.image(f'data:image/png;base64,{chart_image}').classes('w-64 h-64')

ui.run()