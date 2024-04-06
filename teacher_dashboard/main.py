import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import random


ai_feedback_examples = [
    "Consider revisiting the fundamentals of sentence structure to improve clarity.",
    "Great use of vocabulary! Try to focus on verb tenses for better consistency.",
    "To enhance the formality of your language, avoid contractions and colloquialisms.",
    "Watch out for repetitive phrases and try to vary your language use for more impact."
]

df = pd.read_csv('student_data.csv')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Define sidebar styling
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#FFF9C4",  # A good shade of blue
}

# Define main content styling
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# Define sidebar layout
sidebar = html.Div(
    [
        html.H2('Lingomate', style={'textAlign': 'center', 'color': '#007BFF'}),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Class Insights", href="/", active="exact"),
                dbc.NavLink("Student Analysis", href="/student-analysis", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# Define app layout with sidebar and content placeholders
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    html.Div(id="page-content", style=CONTENT_STYLE)
])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/student-analysis":
        return dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Individual Student Analysis"), className="mb-4"),
        dbc.Row([
        dbc.Col([
            html.Label("Select Student"),
            dcc.Dropdown(id="student-dropdown", options=[{'label': name, 'value': name} for name in df['StudentName'].unique()], value=df['StudentName'].unique()[0]),
        ], width=6),
        dbc.Col([
            html.Label("Select Question"),
            dcc.Dropdown(id="question-dropdown", options=[{'label': q, 'value': q} for q in df['Question'].unique()], value=df['Question'].unique()[0]),
        ], width=6),
    ]),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id="error-frequency-histogram"), width=12)
    ]),
    dbc.Row([
        dbc.Col(dash_table.DataTable(
            id='student-performance-table',
            style_cell={'textAlign': 'left', 'paddingBottom': '10px'},  # Left align text, add bottom padding
            style_header={'fontWeight': 'bold'}  # Make headers bold
        ), width=12)
    ]),
        dbc.Row([
        dbc.Col(dcc.Textarea(
            id='feedback-area',
            placeholder="Enter feedback here...",
            value=random.choice(ai_feedback_examples),  # Set a random placeholder feedback from the list
            style={'width': '100%', 'height': '150px'}
        ), width=12),
    ]),
    dbc.Row([
        dbc.Col(html.Button('Submit Feedback', id='submit-feedback', n_clicks=0), width=12)
    ]),
    ])
    
], fluid=True)
    else:  
        return dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Class Performance Dashboard"), className="mb-4")
    ]),
    dcc.Dropdown(
        id='question-dropdown',
        options=[{'label': i, 'value': i} for i in df['Question'].unique()],
        value='Q1'
    ),
     dbc.Row([
        dbc.Col(dcc.Graph(id='grammar-score-heatmap'), width=6),
        dbc.Col(dcc.Graph(id='appropriateness-score-heatmap'), width=6),
    ]),
    dcc.Graph(id='error-analysis-pie')
], fluid=True)

@app.callback(
    [Output('grammar-score-heatmap', 'figure'),
     Output('appropriateness-score-heatmap', 'figure'),
     Output('error-analysis-pie', 'figure')],
    [Input('question-dropdown', 'value')]
)
def update_graphs(selected_question):
    # Filter DataFrame based on selected question
    filtered_df = df[df['Question'] == selected_question]
    
    # Grammar Score Heatmap
    grammar_scores = filtered_df.pivot(index='StudentName', columns='Session', values='GrammarScore')
    fig_grammar = px.imshow(
        grammar_scores, 
        labels=dict(x="Session", y="Student Name", color="Grammar Score"),
        title="Grammar Scores",
        color_continuous_scale="RdYlGn"
    )
    
    # Appropriateness Score Heatmap
    appropriateness_scores = filtered_df.pivot(index='StudentName', columns='Session', values='AppropriatenessScore')
    fig_appropriateness = px.imshow(
        appropriateness_scores, 
        labels=dict(x="Session", y="Student Name", color="Appropriateness Score"),
        title="Appropriateness Scores",
        color_continuous_scale="RdYlGn"
    )
    
    # Common Error Types Pie Chart
    error_counts = filtered_df['TypeCat'].value_counts()
    fig_errors = px.pie(names=error_counts.index, values=error_counts.values, title=f'Common Errors - {selected_question}')
    
    return fig_grammar, fig_appropriateness, fig_errors

@app.callback(
    [Output('student-performance-table', 'data'),
     Output('student-performance-table', 'columns'),
     Output('error-frequency-histogram', 'figure')],
    [Input('student-dropdown', 'value'),
     Input('question-dropdown', 'value')]
)
def update_content(selected_student, selected_question):
    # Filter for the selected student and question
    filtered_df = df[(df['StudentName'] == selected_student) & (df['Question'] == selected_question)]

    # Select the relevant columns to display in the table
    table_data = filtered_df[['Session', 'StudentAnswer', 'GrammarScore', 'AppropriatenessScore']]

    # Set the column names for the DataTable
    columns = [
        {"name": "Session", "id": "Session"},
        {"name": "Student's Answer", "id": "StudentAnswer"},
        {"name": "Grammar Score", "id": "GrammarScore"},
        {"name": "Appropriateness Score", "id": "AppropriatenessScore"},
    ]
    
    # Student-wise error frequency
    student_errors = df[df['StudentName'] == selected_student]['TypeCat'].value_counts().reset_index()
    student_errors.columns = ['Error Type', 'Frequency']  # Renaming columns for clarity

    # Create the histogram with student's error frequency
    fig_errors = px.bar(student_errors, x='Error Type', y='Frequency', title=f'{selected_student} Error Frequency')

    return table_data.to_dict('records'), columns, fig_errors



@app.callback(
    Output('feedback-area', 'placeholder'),
    [Input('student-dropdown', 'value'), Input('question-dropdown', 'value')]
)
def update_placeholder(selected_student, selected_question):
        
    return random.choice(ai_feedback_examples)
    



if __name__ == "__main__":
    app.run_server(debug=True)