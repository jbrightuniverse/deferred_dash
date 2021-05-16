import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from df_render import * 
# can be found at https://github.com/jbrightuniverse/VisualDeferredAcceptance/blob/main/df_render.py

import random
from collections import defaultdict

random.seed(2)
app = dash.Dash(__name__, external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'], title = "Deferred Acceptance", suppress_callback_exceptions=True, update_title=None)



img = super_simple_example([2, 1, 1], 6, 3)
"""
import plotly.graph_objects as go
fig = go.Figure(layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis = {"fixedrange": True, "autorange": False}, yaxis = {"fixedrange": True, "autorange": False}))
fig.add_layout_image(dict(x = 0, sizex = img.width, y = 0, sizey = img.height, xref="x", yref="y", layer="below", sizing="stretch", source = img))
fig.update_xaxes(visible=False, range=(0, img.width))
fig.update_yaxes(visible=False, scaleanchor = "x", range=(img.height, 0))
fig.update_layout(width=img.width, height=img.height, margin={"l": 0, "r": 0, "t": 0, "b": 0})

fig = go.Figure(layout = go.Layout(width = img.width, height = img.height, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis = {"fixedrange": True, "autorange": False}, yaxis = {"fixedrange": True, "autorange": False}, updatemenus = [dict(
            type="buttons",
            buttons=[dict(label="Play",
                          method="animate",
                          args=[None])])]
    ), frames = [go.Frame(layout = fig.layout)] * 10)
fig.add_layout_image(dict(x = 0, sizex = img.width, y = 0, sizey = img.height, xref="x", yref="y", layer="below", sizing="stretch", source = img))
fig.update_xaxes(visible=False, range=(0, img.width))
fig.update_yaxes(visible=False, scaleanchor = "x", range=(img.height, 0))
fig.update_layout(width=img.width, height=img.height, margin={"l": 0, "r": 0, "t": 0, "b": 0})
"""
app.layout = html.Div([
    html.Div(html.A(html.Button("GitHub Source"), href='https://github.com/jbrightuniverse/deferred_dash')),
    html.Br(),
    html.H1("Deferred Acceptance Explained", style={'textAlign': 'center', 'font-family': 'Comic Sans MS', 'color': 'rgb(255, 0, 255)'}),
    html.H5("James Yuming Yu, Vancouver School of Economics", style = {'textAlign': 'center', 'font-family': 'Spectral'}),
    html.Br(),
    html.H6("This interactive page explains how the Deferred Acceptance matching algorithm works."),
    html.H6("Let's suppose we have a school district with students and programs. If you'd like, you can choose how many you want using these sliders:"),
    html.Br(),
    html.Br(),
    html.Div([
        html.Div([html.H5("Move this slider to choose a number of students →", style={'textAlign': 'center'})], className = "six columns"),
        html.Div([html.Br(), dcc.Slider(
            id='slider1',
            min=1,
            max=10,
            step=1,
            value=6,
            marks={i: str(i) for i in range(1, 11)}
        )], className = "six columns")],
        className = "row"),
    html.Div([
        html.Div([html.H5("Move this slider to choose a number of programs →", style={'textAlign': 'center'})], className = "six columns"),
        html.Div([html.Br(), dcc.Slider(
            id='slider2',
            min=3,
            max=5,
            step=1,
            value=3,
            marks={i: str(i) for i in range(3, 6)}
        )], className = "six columns")],
        className = "row"),
    html.Div([
        html.Div([html.Br(), html.Br(), html.H5("Click the tabs to change program capacities →", style={'textAlign': 'center'})], className = "six columns"),
        html.Div([
        dcc.Tabs(style = {'height': '44px'}, children = [
        dcc.Tab(label=f"Program {i}", id = f"tab_p{i}", children = html.Div([
            html.Br(),
            html.P(f"Move the slider to change capacity of Program {i}", style={'textAlign': 'center'}),
            dcc.Slider(
                id=f"slider_p{i}",
                min=1,
                max=2,
                step=1,
                value=[2, 1][i > 1],
                marks={j: str(j) for j in range(1, 4)}
            ),
        ]), disabled = i > 3) for i in range(1, 6)]),
        ], className = "six columns")
    ], className = "row"),
    html.H6("You can see the results of the sliders below. Blue circles are students, green boxes are programs, and black outlines are seats in the programs.", style={'textAlign': 'center'}),
    html.Div([html.Img(src = process(img), id = "img")], style={'textAlign': 'center'}, id = "b"),
    dcc.Store(id = "students"),
    dcc.Store(id = "schools"),
    dcc.Store(id = "capacity", data = [2, 1, 1, 1, 1]),
    html.Div([
        html.Div([html.Br()], className = "one column"),   
        html.Div([
            html.P("Our objective is to place students in these programs such that everyone's preferences (that is, their choices) are met as closely as possible."),
            html.P("To do this, we first need to catch these preferences. Suppose we tell the students' parents to fill out application forms for these programs, where we ask them to provide their top three choices along with the equivalent of Student ID. The form should output to an Excel spreadsheet which should look something like the one on the right."),
            html.P("Notice how some students are missing entries — often parents don't actually fill out all three choices, as perhaps they only want to apply for one program. Nonetheless, the algorithm is capable of using any length of choices given to it."),
            html.P("(Small note: The values for Choice 1, Choice 2 and Choice 3 in this webpage are randomized when you add Program 4 or Program 5 (to allow the students to specify them).)")
        ], className = "five columns"),
        html.Div([ 
        dash_table.DataTable(
            id='student_form',
            style_cell = {'font-family':'Calibri', 'textAlign': 'left'},
            style_header = {'font-family': 'Calibri', 'textAlign': 'center', 'fontWeight': 'bold'},
            style_data_conditional=[{"if": {"state": "selected"}, "backgroundColor": "inherit !important", "border": "inherit !important"}],  
            columns=[{"name": i, "id": i} for i in ["Name", "ID", "Address", "Choice 1", "Choice 2", "Choice 3"]],
            data=[{"Name": "Student 1", "ID": 1, "Address": "1234 Random Name Way, Vancouver, BC", "Choice 1": "Program 1", "Choice 2": "Program 2", "Choice 3": "Program 3"},
                {"Name": "Student 2", "ID": 2, "Address": "2-555 Arbitrary Street, Vancouver, BC", "Choice 1": "Program 2", "Choice 2": "Program 3", "Choice 3": "Program 1"},
                {"Name": "Student 3", "ID": 3, "Address": "42 Anywhere Road, Vancouver, BC", "Choice 1": "Program 3", "Choice 2": "Program 1"},
                {"Name": "Student 4", "ID": 4, "Address": "12005 Placeholder Boulevard, Richmond, BC", "Choice 1": "Program 2", "Choice 2": "Program 1", "Choice 3": "Program 3"},
                {"Name": "Student 5", "ID": 5, "Address": "876 Someplace Avenue, Burnaby, BC", "Choice 1": "Program 1"},
                {"Name": "Student 6", "ID": 6, "Address": "96 Nowhere Highway, Vancouver BC", "Choice 1": "Program 1", "Choice 2": "Program 2"}],
        )], className = "five columns"),
        html.Div([html.Br()], className = "one column")   
    ], className = "row"),
    html.Br(),
    html.Div([
            html.H6("Given the form, we want to determine a ranking mechanism for programs (i.e. obtain their own preferences).", style={'textAlign': 'center'}),
            html.H6("Normally, school districts have particular preferences over who they prefer to accept — notably, students are usually prioritized if they have a sibling already in the school, and from there priorities are based on catchment relative to the program.", style={'textAlign': 'center'}),
            html.H6("To obtain the preferences of these programs, we need to figure out where siblings are and what the relative catchments are.", style={'textAlign': 'center'})
    ]),
    html.Div([
        html.Div([html.Br()], className = "one column"),
        html.Div([ 
        dash_table.DataTable(
            id='catchment_table',
            style_as_list_view=True,
            style_header={
                'font-family':'Calibri',
                'backgroundColor': 'white',
                'color': 'black',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {"if": {"state": "selected"}, "backgroundColor": "inherit !important", "border": "inherit !important"},
                {
                    'if': {'row_index': 'odd'},
                    'font-family':'Calibri',
                    'backgroundColor': 'rgb(94, 247, 235)',
                    'color': 'black'
                },
                {
                    'if': {'row_index': 'even'},
                    'font-family':'Calibri',
                    'backgroundColor': 'rgb(247, 94, 94)',
                    'color': 'white'
                }
            ],
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ["Address"]
            ],
            columns=[{"name": i, "id": i} for i in ["Address", "Catchment Zone"]],
            data=[{"Address": "1234 Random Name Way, Vancouver, BC", "Catchment Zone": "Catchment 1"},
                {"Address": "2-555 Arbitrary Street, Vancouver, BC", "Catchment Zone": "Catchment 1"},
                {"Address": "42 Anywhere Road, Vancouver, BC", "Catchment Zone": "Catchment 2"},
                {"Address": "12005 Placeholder Boulevard, Richmond, BC", "Catchment Zone": "Out-of-District"},
                {"Address": "876 Someplace Avenue, Burnaby, BC", "Catchment Zone": "Out-of-District"},
                {"Address": "96 Nowhere Highway, Vancouver BC", "Catchment Zone": "Catchment 1"}],
        )], className = "three columns"), 
        html.Div([
            html.Br(),
            html.P("Suppose an existing process employed by school districts is used to determine which catchment zone a student's address is in. The process may return data like that of the table on the left."),
            html.Br(),
            html.P("Also suppose we use an existing process to determine if students have siblings. This would return data like the table on the right.", style = {"textAlign": "right"})
        ], className = "four columns"),
        html.Div([ 
        dash_table.DataTable(
            id='sibling_table',
            style_as_list_view=True,
            style_header={
                'font-family':'Calibri',
                'backgroundColor': 'white',
                'color': 'black',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {"if": {"state": "selected"}, "backgroundColor": "inherit !important", "border": "inherit !important"},
                {
                    'if': {'row_index': 'odd'},
                    'font-family':'Calibri',
                    'backgroundColor': 'rgb(94, 247, 235)',
                    'color': 'black'
                },
                {
                    'if': {'row_index': 'even'},
                    'font-family':'Calibri',
                    'backgroundColor': 'rgb(247, 94, 94)',
                    'color': 'white'
                }
            ],
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ["Name"]
            ],
            columns=[{"name": i, "id": i} for i in ["Name", "Sibling 1", "Sibling 2", "Sibling 3"]],
            data=[{"Name": "Student 1", "Sibling 1": "Student 11"},
                  {"Name": "Student 2", "Sibling 1": "Student 12"},
                  {"Name": "Student 3"},
                  {"Name": "Student 4", "Sibling 1": "Student 13"},
                  {"Name": "Student 5"},
                  {"Name": "Student 6", "Sibling 1": "Student 14"}],
        )], className = "three columns"), 
        html.Div([html.Br()], className = "one column")
    ], className = "row"),
    html.Br(),
    html.H5("By updating the original Excel sheet with these two results, we get the following:", style = {"textAlign": "center"}),
    html.Div([
        html.Div([html.Br()], className = "one column"),   
        html.Div([ 
        dash_table.DataTable(
            id='student_form_2',
            style_cell = {'font-family':'Calibri', 'textAlign': 'left'},
            style_header = {'font-family': 'Calibri', 'textAlign': 'center', 'fontWeight': 'bold'},
            style_data_conditional=[{"if": {"state": "selected"}, "backgroundColor": "inherit !important", "border": "inherit !important"}],  
            columns=[{"name": i, "id": i} for i in ["Name", "ID", "Catchment", "Choice 1", "Choice 2", "Choice 3", "Siblings"]],
            data=[{"Name": "Student 1", "ID": 1, "Catchment": "Catchment 1", "Choice 1": "Program 1", "Choice 2": "Program 2", "Choice 3": "Program 3", "Siblings": "Student 11"},
                {"Name": "Student 2", "ID": 2, "Catchment": "Catchment 1", "Choice 1": "Program 2", "Choice 2": "Program 3", "Choice 3": "Program 1", "Siblings": "Student 12"},
                {"Name": "Student 3", "ID": 3, "Catchment": "Catchment 2", "Choice 1": "Program 3", "Choice 2": "Program 1"},
                {"Name": "Student 4", "ID": 4, "Catchment": "Out-of-District", "Choice 1": "Program 2", "Choice 2": "Program 1", "Choice 3": "Program 3", "Siblings": "Student 13"},
                {"Name": "Student 5", "ID": 5, "Catchment": "Out-of-District", "Choice 1": "Program 1"},
                {"Name": "Student 6", "ID": 6, "Catchment": "Catchment 1", "Choice 1": "Program 1", "Choice 2": "Program 2", "Siblings": "Student 14"}],
        )], className = "ten columns"),
        html.Div([html.Br()], className = "one column")   
    ], className = "row"),
    html.Br(),
    html.H5("Now we make a sheet for the programs with name, catchment region, priorities and a list of existing students (so we can track siblings).", style = {"textAlign": "center"}),
    html.Div([
        html.Div([html.Br()], className = "one column"),   
        html.Div([ 
        dash_table.DataTable(
            id='school_form',
            style_cell = {'font-family':'Calibri', 'textAlign': 'left'},
            style_header = {'font-family': 'Calibri', 'textAlign': 'center', 'fontWeight': 'bold'},
            style_data_conditional=[{"if": {"state": "selected"}, "backgroundColor": "inherit !important", "border": "inherit !important"}],  
            columns=[{"name": i, "id": i} for i in ["Name", "Catchment", "Priorities", "Existing Students"]],
            data=[{"Name": "Program 1", "Catchment": "Catchment 1", "Priorities": "Sibling, Catchment", "Existing Students": "Student 11, Student 13"},
                {"Name": "Program 2", "Catchment": "Catchment 2", "Priorities": "Sibling, Catchment", "Existing Students": "Student 12, Student 14"},
                {"Name": "Program 3", "Catchment": "Catchment 1", "Priorities": "Sibling, Catchment", "Existing Students": "Student 15, Student 16, Student 17"}
                ],
        )], className = "ten columns"),
        html.Div([html.Br()], className = "one column")   
    ], className = "row"),
    html.Br(),
    html.Div([
        html.Div([html.Br()], className = "one column"),   
        html.Div([
            html.P("In the above sheet, some programs could have priorities in a different order. This order matters: if Sibling is first, a school will prioritize siblings regardless of catchment before checking for catchment, and if Sibling is not first, a school will prioritize catchment regardless of siblings before checking for siblings."),
            html.P("Given this data, we can determine how programs prefer students. To do this, each program evaluates a student's catchment and checks their siblings to determine how to prioritize them."),
            html.P("(For simplicity, we let each program rank every student, but technically only the students with that program on their form need to be ranked by said program.)")
        ], className = "ten columns"),
        html.Div([html.Br()], className = "one column")
    ], className = "row"),
    html.Br(),
    html.Div([
        html.Div([html.Br()], className = "one column"),   
        html.Div([ 
        dash_table.DataTable(
            id='school_form_big',
            style_cell = {'font-family':'Calibri', 'textAlign': 'left'},
            style_header = {'font-family': 'Calibri', 'textAlign': 'center', 'fontWeight': 'bold'},
            style_data_conditional=[{"if": {"state": "selected"}, "backgroundColor": "inherit !important", "border": "inherit !important"}],  
            columns=[{"name": i, "id": i} for i in ["Program", "Student Being Ranked", "Relative Catchment", "Shared Siblings?"]],
            data=[{"Program": "Program 1", "Student Being Ranked": "Student 1", "Relative Catchment": "Local", "Shared Siblings?": "yes"},
            {"Student Being Ranked": "Student 2", "Relative Catchment": "Local", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 3", "Relative Catchment": "Nonlocal", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 4", "Relative Catchment": "Out-of-District", "Shared Siblings?": "yes"},
            {"Student Being Ranked": "Student 5", "Relative Catchment": "Out-of-District", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 6", "Relative Catchment": "Local", "Shared Siblings?": "no"},
            {},
            {"Program": "Program 2", "Student Being Ranked": "Student 1", "Relative Catchment": "Nonlocal", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 2", "Relative Catchment": "Nonlocal", "Shared Siblings?": "yes"},
            {"Student Being Ranked": "Student 3", "Relative Catchment": "Local", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 4", "Relative Catchment": "Out-of-District", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 5", "Relative Catchment": "Out-of-District", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 6", "Relative Catchment": "Nonlocal", "Shared Siblings?": "yes"},
            {},
            {"Program": "Program 3", "Student Being Ranked": "Student 1", "Relative Catchment": "Local", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 2", "Relative Catchment": "Local", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 3", "Relative Catchment": "Nonlocal", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 4", "Relative Catchment": "Out-of-District", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 5", "Relative Catchment": "Out-of-District", "Shared Siblings?": "no"},
            {"Student Being Ranked": "Student 6", "Relative Catchment": "Local", "Shared Siblings?": "no"},
                ],
        )], className = "ten columns"),
        html.Div([html.Br()], className = "one column")   
    ], className = "row"),
    html.Br(),
    html.Div([
        html.Div([html.Br()], className = "one column"),   
        html.Div([
            html.P("To generate the \"Relative Catchment\" column, we simply check if the catchment of each student is the same or not the same as that of the program."),
            html.P("To generate the \"Shared Siblings?\" column, we simply check if there is at least one person in common between the list of each student's siblings and the list of students already in a program."),
            html.P("We can now construct the actual preferences of each program. This is done by applying the different priority rankings (Siblings and Catchment) to the above table to order the students by the properties we found. The results of this ordering can be found in the sheet on the right."),
            html.P("The numbers in the \"Preference\" column correspond to the IDs of each student (which are also their names here), and the leftmost students are preferred to the rightmost students (that is, the first student is most preferred)."),
            html.P("You can click the tabs on the window underneath the table on the right to observe how each program actually ranks students. When two students are equally preferred, we place them into the same \"priority group\" and then randomly choose one of them to be more preferable."),
            html.P("The number in brackets (e.g. (1)) corresponds to the overall preference order of these priority groups. For example, every student in group (1) is more preferred than every student in group (2). Every student within group (1) is equally preferred to every other student in group (1).")
            ], className = "five columns"),
            html.Div([ 
        dash_table.DataTable(
            id='pref_form',
            style_cell = {'font-family':'Calibri', 'textAlign': 'left'},
            style_header = {'font-family': 'Calibri', 'textAlign': 'center', 'fontWeight': 'bold'},
            style_data_conditional=[{"if": {"state": "selected"}, "backgroundColor": "inherit !important", "border": "inherit !important"}],  
            columns=[{"name": i, "id": i} for i in ["Name", "Priorities", "Preference"]],
            data=[{"Name": "Program 1", "Priorities": "Sibling, Catchment", "Preference": "1, 4, 2, 6, 3, 5"},
                {"Name": "Program 2", "Priorities": "Sibling, Catchment", "Preference": "2, 6, 3, 1, 4, 5"},
                {"Name": "Program 3", "Priorities": "Sibling, Catchment", "Preference": "1, 2, 6, 3, 4, 5"}
                ],
        ),
        html.Br(),
        html.H6("Click the tabs to view priority groups for each program", style = {'textAlign': 'center'}),
        html.Br(),
        dcc.Tabs(style = {'height': '44px'}, children = [
        dcc.Tab(label=f"Pgm {i}", id = f"tab2_p{i}", children = html.Div([
            html.Br(),
            html.Div([html.Img(id = f"img_{i}")], style={'textAlign': 'center'}, id = f"b{i}"),
        ]), disabled = i > 3) for i in range(1, 6)]),
        ], className = "five columns"),
        html.Div([html.Br()], className = "one column")
    ], className = "row"),
    html.Br(),
    html.H5("Now that we have preferences for both students and programs, we can run the algorithm.", style = {'textAlign': 'center'}),
    html.H5("The algorithm can be generalized as follows:", style = {'textAlign': 'center'}),
    html.Br(),
    html.Div([
        html.Div([html.Br()], className = "two columns"),   
        html.Div([
            html.H6("- Take the first choice program of every student and try to assign the student to that program."),
            html.H6("--------- If the program has space, let them in."),
            html.H6("--------- Otherwise if the program is full, check if the program prefers this student to any already accepted."),
            html.H6("------------------- If the student is preferable, reject a less-preferable student."),
            html.H6("------------------- Otherwise, reject this student."),
            html.H6("------------------- The less-preferable student, whomever it is, now re-applies with their second choice."),
            html.H6("- Repeat the above process until everyone is either accepted or out of choices to apply to.")

        ], className = "eight columns"),
        html.Div([html.Br()], className = "one column"),   
    ], className = "row"),
    html.Br(),
    html.H5("You can use the following interactive widget to explore this algorithm applied to the data you entered (first frame may take a few seconds to load):", style = {'textAlign': 'center'}),
    html.Br(),
    html.Div([
        html.Img(id = "img2", src = process(img)),
        html.Div([
            html.Div([html.Br()], className = "three columns"),  
            html.Div([html.Button('PREV', id='prev')], className = "three columns"),
            html.Div([html.Button('NEXT', id='next')], className = "three columns"),
            html.Div([html.Br()], className = "three columns"),  
            ], className = "row"),
        dcc.Loading(children=[html.Div([html.H5("Initial Stage. Press NEXT to continue.", id = "text")])], type = "circle"),
        html.H5(id = "text2"),
        ], style={'textAlign': 'center'}, id = "bq3"),
    dcc.Store(id = "s_application"),
    dcc.Store(id = "p_data"),
    dcc.Store(id = "prefs"),
    dcc.Store(id = "imgs", data = []),
    dcc.Store(id = "texts", data = []),
    dcc.Store(id = "framebuffer", data = -1),
    html.H4("Through this animation, it becomes clear why the algorithm is called 'deferred' acceptance, as acceptances are not finalized until the preferences of every student have been considered (in order to search for potentially more beneficial assignments).", style = {"textAlign": "center"}),
    html.Br(),
    html.Br(),
    html.H1("Algorithm Extension: Change of Mind", style = {"textAlign": "center", 'font-family': 'Comic Sans MS'}),
    html.H5("What if a student's parent were to have second thoughts and decide not to accept their offer? The algorithm can easily be extended to account for this.", style = {"textAlign": "center"}),
    html.Br(),
    html.H6("First, run the algorithm like in the above animation. Then, remove the quitting student."),
    html.H6("This opens up a new slot in one of the programs. Find all the students everywhere that prefer this new slot to their existing slot (which includes the case where they may not have a slot at all)."),
    html.H6("Get the program to pick their most preferred student out of this new list. Give them an offer to join."),
    html.H6("To keep things on time, give them a few days to respond. If they don't, send the offer to the next best student, and so on until we run out of students (if we run out, nobody wants the seat, so it remains empty)."),
    html.H6("But if someone accepts, assign that student to take that seat."),
    html.H6("Now, if that student didn't have a seat before, we are done, but if they did, there is now a new open seat in their old program. Go back to the 'opens up a new slot' step with the new open seat."),
    html.H6("That's all. Conduct the same auto-adjustment procedure every time someone quits."),
    html.Br(),
    html.Br(),
    html.H1("Algorithm Extension: Late Entry", style = {"textAlign": "center", 'font-family': 'Comic Sans MS'}),
    html.H6("If a student decides to fill out the form late, and late entries are being accepted, add them to the pool of unassigned students.", style = {"textAlign": "center"}),
    html.H6("If a slot opens up from a student quitting, follow the instructions from the 'Change of Mind' extension with this new student included. That's all.", style = {'textAlign': 'center'}),
    html.Br(),
    html.Br()
])

@app.callback(Output("p_data", "data"), Output("s_application", "data"), Output("prefs", "data"), 
Output("img_1", "src"), Output("img_2", "src"), Output("img_3", "src"), Output("img_4", "src"), Output("img_5", "src"), 
            Output("pref_form", "data"), Output("school_form_big", "data"), Output("school_form", "data"), 
            Output("student_form_2", "data"), Output("sibling_table", "data"), Output("catchment_table", "data"), 
            Output("students", "data"), Output("student_form", "data"), Output("schools", "data"), 
            Output("tab_p4", "disabled"), Output("tab_p5", "disabled"), Output("tab2_p4", "disabled"), Output("tab2_p5", "disabled"), Output("next", "n_clicks"), Input("slider1", "value"), Input("slider2", "value"), Input("capacity", "data"))
def get_everything(val_first, val, caps):
    maximum_students = [
        {"Name": "Student 1", "ID": 1, "Address": "1234 Random Name Way, Vancouver, BC", "Choice 1": "Program 1", "Choice 2": "Program 2", "Choice 3": "Program 3"},
        {"Name": "Student 2", "ID": 2, "Address": "2-555 Arbitrary Street, Vancouver, BC", "Choice 1": "Program 2", "Choice 2": "Program 3", "Choice 3": "Program 1"},
        {"Name": "Student 3", "ID": 3, "Address": "42 Anywhere Road, Vancouver, BC", "Choice 1": "Program 3", "Choice 2": "Program 1"},
        {"Name": "Student 4", "ID": 4, "Address": "12005 Placeholder Boulevard, Richmond, BC", "Choice 1": "Program 2", "Choice 2": "Program 1", "Choice 3": "Program 3"},
        {"Name": "Student 5", "ID": 5, "Address": "876 Someplace Avenue, Burnaby, BC", "Choice 1": "Program 1"},
        {"Name": "Student 6", "ID": 6, "Address": "96 Nowhere Highway, Vancouver BC", "Choice 1": "Program 1", "Choice 2": "Program 2"},
        {"Name": "Student 7", "ID": 7, "Address": "336 Hidden Drive, Vancouver, BC", "Choice 1": "Program 3", "Choice 2": "Program 2"},
        {"Name": "Student 8", "ID": 8, "Address": "75000 Far Flung Place, Surrey, BC", "Choice 1": "Program 2", "Choice 2": "Program 3", "Choice 3": "Program 1"},
        {"Name": "Student 9", "ID": 9, "Address": "620 Missing Crescent, Vancouver, BC", "Choice 1": "Program 3"},
        {"Name": "Student 10", "ID": 10, "Address": "2000 Gaussian Circle, Vancouver, BC", "Choice 1": "Program 3", "Choice 2": "Program 1", "Choice 3": "Program 2"}
    ]
    addresses = [
        {"Address": "1234 Random Name Way, Vancouver, BC", "Catchment Zone": "Catchment 1"},
        {"Address": "2-555 Arbitrary Street, Vancouver, BC", "Catchment Zone": "Catchment 1"},
        {"Address": "42 Anywhere Road, Vancouver, BC", "Catchment Zone": "Catchment 2"},
        {"Address": "12005 Placeholder Boulevard, Richmond, BC", "Catchment Zone": "Out-of-District"},
        {"Address": "876 Someplace Avenue, Burnaby, BC", "Catchment Zone": "Out-of-District"},
        {"Address": "96 Nowhere Highway, Vancouver BC", "Catchment Zone": "Catchment 1"},
        {"Address": "336 Hidden Drive, Vancouver, BC", "Catchment Zone": "Catchment 3"},
        {"Address": "75000 Far Flung Place, Surrey, BC", "Catchment Zone": "Out-of-District"},
        {"Address": "620 Missing Crescent, Vancouver, BC", "Catchment Zone": "Catchment 4"},
        {"Address": "2000 Gaussian Circle, Vancouver, BC", "Catchment Zone": "Catchment 4"}
    ]
    siblings = [
        {"Name": "Student 1", "Sibling 1": "Student 11"},
        {"Name": "Student 2", "Sibling 1": "Student 12"},
        {"Name": "Student 3"},
        {"Name": "Student 4", "Sibling 1": "Student 13"},
        {"Name": "Student 5"},
        {"Name": "Student 6", "Sibling 1": "Student 14"},
        {"Name": "Student 7", "Sibling 1": "Student 15", "Sibling 2": "Student 16", "Sibling 3": "Student 17"},
        {"Name": "Student 8"},
        {"Name": "Student 9", "Sibling 1": "Student 18", "Sibling 2": "Student 19"},
        {"Name": "Student 10", "Sibling 1": "Student 20"}]

    form2 = [
        {"Name": "Student 1", "ID": 1, "Catchment": "Catchment 1", "Choice 1": "Program 1", "Choice 2": "Program 2", "Choice 3": "Program 3", "Siblings": "Student 11"},
        {"Name": "Student 2", "ID": 2, "Catchment": "Catchment 1", "Choice 1": "Program 2", "Choice 2": "Program 3", "Choice 3": "Program 1", "Siblings": "Student 12"},
        {"Name": "Student 3", "ID": 3, "Catchment": "Catchment 2", "Choice 1": "Program 3", "Choice 2": "Program 1"},
        {"Name": "Student 4", "ID": 4, "Catchment": "Out-of-District", "Choice 1": "Program 2", "Choice 2": "Program 1", "Choice 3": "Program 3", "Siblings": "Student 13"},
        {"Name": "Student 5", "ID": 5, "Catchment": "Out-of-District", "Choice 1": "Program 1"},
        {"Name": "Student 6", "ID": 6, "Catchment": "Catchment 1", "Choice 1": "Program 1", "Choice 2": "Program 2", "Siblings": "Student 14"},
        {"Name": "Student 7", "ID": 7, "Catchment": "Catchment 3", "Choice 1": "Program 3", "Choice 2": "Program 2", "Siblings": "Student 15, Student 16, Student 17"},
        {"Name": "Student 8", "ID": 8, "Catchment": "Out-of-District", "Choice 1": "Program 2", "Choice 2": "Program 3", "Choice 3": "Program 1"},
        {"Name": "Student 9", "ID": 9, "Catchment": "Catchment 4", "Choice 1": "Program 3", "Siblings": "Student 18, Student 19"},
        {"Name": "Student 10", "ID": 10, "Catchment": "Catchment 4", "Choice 1": "Program 3", "Choice 2": "Program 1", "Choice 3": "Program 2", "Siblings": "Student 20"}
    ]

    sform = [
        {"Name": "Program 1", "Catchment": "Catchment 1", "Priorities": "Sibling, Catchment", "Existing Students": "Student 11, Student 13"},
        {"Name": "Program 2", "Catchment": "Catchment 2", "Priorities": "Sibling, Catchment", "Existing Students": "Student 12, Student 14"},
        {"Name": "Program 3", "Catchment": "Catchment 1", "Priorities": "Sibling, Catchment", "Existing Students": "Student 15, Student 16, Student 17"},
        {"Name": "Program 4", "Catchment": "Catchment 3", "Priorities": "Catchment, Sibling", "Existing Students": "Student 18, Student 19"},
        {"Name": "Program 5", "Catchment": "Catchment 4", "Priorities": "Catchment, Sibling", "Existing Students": "Student 20"}
    ]

    convenience = {}

    sformbig = []
    for i in range(1, val + 1):
        convenience[f"Program {i}"] = {}
        seen = False
        lcatchment = None
        lstudents = []
        for d in sform:
            if d["Name"] == f"Program {i}":
                lcatchment = d["Catchment"]
                lstudents = [b.rstrip().lstrip() for b in d["Existing Students"].split(",")]
                break
        # for each program, generate form
        for j in range(1, val_first + 1):
            student = {}
            if not seen:
                seen = True
                student["Program"] = f"Program {i}"
            # iterate over each student
            student["Student Being Ranked"] = f"Student {j}"
            catchment = None
            lsiblings = []
            for d in form2:
                if d["Name"] == f"Student {j}":
                    catchment = d["Catchment"]
                    if "Siblings" in d:
                        lsiblings = [b.rstrip().lstrip() for b in d["Siblings"].split(",")]
                    break
            if catchment == "Out-of-District":
                student["Relative Catchment"] = "Out-of-District"
            else:
                student["Relative Catchment"] = ["Nonlocal", "Local"][catchment == lcatchment]

            student["Shared Siblings?"] = ["no", "yes"][len(set(lsiblings).intersection(lstudents)) > 0]
            convenience[f"Program {i}"][f"Student {j}"] = {"Sibling": student["Shared Siblings?"], "Catchment": student["Relative Catchment"]}
            sformbig.append(student)
        if i != val:
            sformbig.append({})

    constraints = {
        "Sibling": ["yes", "no"],
        "Catchment": ["Local", "Nonlocal", "Out-of-District"]
    }

    conversion = {
        "yes": "Sibling",
        "no": "No Sibling",
        "Local": "Local",
        "Nonlocal": "Nonlocal",
        "Out-of-District": "Out-of-District"
    }

    pform = []
    all_ordered_groups = {}
    program_preferences = {}
    priority_group_dict = {}

    def generate_preferences(students, conditions):
        """Generates the preferences of a school over students."""
        priority_groups = defaultdict(list)
        for name in students:
            priority_groups[",".join([conversion[students[name][cond_name]] for cond_name in conditions])].append(name) 
        return dict(priority_groups)

    for i in range(1, val + 1):
        ordered_groups = [""]
        priorities = []
        for d in sform:
            if d["Name"] == f"Program {i}":
                priorities = d["Priorities"].split(", ")
                break
        for guideline in priorities:
            new_copies = []
            for base in ordered_groups:
                for option in constraints[guideline]:
                    new_copies.append(base + [",", ""][base == ""] + conversion[option])
            ordered_groups = new_copies

        student_characteristics = convenience[f"Program {i}"]
        priority_groups = generate_preferences(student_characteristics, priorities)
        for priority_group in priority_groups:
            random.shuffle(priority_groups[priority_group])
            
        # save data for later
        priority_group_dict[f"Program {i}"] = priority_groups
        ordered_students = []
        for group in ordered_groups:
            if group in priority_groups:
                ordered_students += priority_groups[group]
        
        program_preferences[f"Program {i}"] = ordered_students
        all_ordered_groups[f"Program {i}"] = ordered_groups
        pform.append({"Name": f"Program {i}", "Priorities": ", ".join(priorities), "Preference": ", ".join([a.split(" ")[1] for a in ordered_students])})

    data = maximum_students[:val_first]
    res = addresses[:val_first]
    sib = siblings[:val_first]
    wform2 = form2[:val_first]
    wsform = sform[:val]
    imgs = priority_group_example(all_ordered_groups, priority_group_dict, [f"Program {i}" for i in range(1, val + 1)])
    imgs = [process(im) for im in imgs]
    while len(imgs) != 5:
        imgs.append(None)
    
    choices = ["Choice 1", "Choice 2", "Choice 3"]
    # adjust preferences of students when changing number of schools
    base = ["Program 1", "Program 2", "Program 3"]
    
    if val == 3:
        for student in data:
            for choice in choices:
                if choice in student and student[choice] not in base:
                    # resample 
                    selection = random.sample(base, random.randrange(1, 4))
                    for i, entry in enumerate(selection):
                        student[choices[i]] = entry
                    break # only need to resample once

    elif val == 4:
        for student in data:
            for choice in choices:
                if choice in student and student[choice] not in base + ["Program 4"]:
                    # resample if a Program 5 is found
                    selection = random.sample(base + ["Program 4"], random.randrange(1, 4))
                    for i, entry in enumerate(selection):
                        student[choices[i]] = entry
                    break # only need to resample once
            else:
                # did not resample, attempt to randomly insert a Program 4
                my_choices = [student[choice] for choice in student if choice in choices]
                if "Program 4" not in my_choices:
                    ind = random.randrange(2*len(my_choices))
                    if ind < len(my_choices):
                        # half probability of accepting to a random slot that exists
                        student[choices[ind]] = "Program 4"

    elif val == 5:
        for student in data:
            # attempt to randomly insert Program 4
            my_choices = [student[choice] for choice in student if choice in choices]
            if "Program 4" not in my_choices:
                ind = random.randrange(2*len(my_choices))
                if ind < len(my_choices):
                    # half probability of accepting to a random slot that exists
                    student[choices[ind]] = "Program 4"
            # attempt Program 5
            if "Program 5" not in my_choices:
                ind = random.randrange(2*len(my_choices))
                if ind < len(my_choices):
                    # half probability of accepting to a random slot that exists
                    # may override Program 4, may not
                    student[choices[ind]] = "Program 5"

    
    capacitydict = {f"Program {i}": {"capacity": caps[i-1]} for i in range(1, val + 1)}
    student_application_forms = {student["Name"]: {"form": [student[choice] for choice in student if choice in choices]} for student in data}
    return capacitydict, student_application_forms, program_preferences, imgs[0], imgs[1], imgs[2], imgs[3], imgs[4], pform, sformbig, wsform, wform2, sib, res, val_first, data, val, val <= 3, val <= 4, val <= 3, val <= 4, 0

@app.callback(Output("capacity", "data"), Input("capacity", "data"), 
Input(f"slider_p1", "value"), Input(f"slider_p2", "value"), Input(f"slider_p3", "value"), Input(f"slider_p4", "value"), Input(f"slider_p5", "value"))
def get_cap(data, val1, val2, val3, val4, val5):
    data = [val1, val2, val3, val4, val5]
    return data

@app.callback(Output("img", "src"), Input("capacity", "data"), Input("students", "data"), Input("schools", "data"))
def update_students(data, students, schools):
    return super_simple_example(data, students, schools)

@app.callback(Output("framebuffer", "data"), Output("img2", "src"), Output("text", "children"), Output("imgs", "data"), Output("texts", "data"),
Input("imgs", "data"), Input("texts", "data"),Input("p_data", "data"), Input("s_application", "data"), Input("prefs", "data"), 
Input("capacity", "data"), Input("students", "data"), Input("schools", "data"),
Input("next", "n_clicks"), Input("prev", "n_clicks"), Input("framebuffer", "data"))
def get_button(imgs, texts, capacitydict, student_application_forms, program_preferences, data, students, schools, click, click2, framebuffer):
    ctx = dash.callback_context
    if not click or click == 0:
        return framebuffer, super_simple_example(data, students, schools), "Initial Stage. Press NEXT to continue.", [], []
    elif click == 1 or (click > 1 and framebuffer == -1):
        state = [1, 1]
        imgs = []
        texts = []
        while state[0] != None:
            state = localized_render_stage(state = state, form = student_application_forms, program_data = capacitydict, pref = program_preferences)
            if state[0] != None:
                imgs.extend(state[0])
            else:
                imgs.extend(state[1])
            texts.extend(["Starting from top of available student list."] + state[2])
        del texts[0]
        return 1, imgs[0], texts[0], imgs, texts
    if ctx:
        which = ctx.triggered[0]['prop_id'].split('.')[0]
        if which == "next" and framebuffer < len(imgs) - 1:
            framebuffer += 1
        elif which == "prev" and framebuffer > 0:
            framebuffer -= 1
    return framebuffer, imgs[framebuffer], texts[framebuffer], imgs, texts

PUT_HOST = "REPLACE.REPLACE.REPLACE.REPLACE"
PUT_PORT = 8080

if __name__ == "__main__":
    app.run_server(use_reloader=False, debug = False, host = PUT_HOST, port =  PUT_PORT)