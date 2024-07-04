import networkx as nx
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

# Generate a random graph
def generate_random_graph(num_nodes, num_edges, graph_type):
    if graph_type == 'erdos_renyi':
        G = nx.erdos_renyi_graph(num_nodes, num_edges)
    elif graph_type == 'barabasi_albert':
        if isinstance(num_edges, float):
            num_edges = int(num_edges)
        G = nx.barabasi_albert_graph(num_nodes, num_edges)
    elif graph_type == 'watts_strogatz':
        if isinstance(num_edges, float):
            num_edges = int(num_edges)
        G = nx.watts_strogatz_graph(num_nodes, num_edges, 0.3) # p metric is already filled
    elif graph_type == 'random_geometric':
        G = nx.random_geometric_graph(num_nodes, 0.3) #radius is already selected
    elif graph_type == 'connected_caveman':
        if isinstance(num_edges, float):
            num_edges = int(num_edges)
        G = nx.connected_caveman_graph(num_nodes, num_edges // num_nodes) #cliques 
    else:
        G = nx.erdos_renyi_graph(num_nodes, num_edges)  # Default to Erdős-Rényi graph
    return G

# Create a Dash application
app = dash.Dash(__name__)

# Custom CSS styles
external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/lux/bootstrap.min.css']

# Layout for Dash application
app.layout = html.Div(style={'font-family': 'Arial, sans-serif', 'background-color': '#f8f9fa', 'color': '#495057', 'padding': '20px'}, children=[
    html.H1('GRAPHY', style={'text-align': 'center', 'color': '#007bff', 'font-size': '36px', 'margin-bottom': '20px'}),

    html.Div([
        html.Div([
            html.Label('Graph Type:', style={'font-weight': 'bold', 'font-size': '18px'}),
            dcc.Dropdown(
                id='dropdown-graph-type',
                options=[
                    {'label': 'Erdős-Rényi', 'value': 'erdos_renyi'},
                    {'label': 'Barabási-Albert', 'value': 'barabasi_albert'},
                    {'label': 'Watts-Strogatz', 'value': 'watts_strogatz'},
                    {'label': 'Random Geometric', 'value': 'random_geometric'},
                    {'label': 'Connected Caveman', 'value': 'connected_caveman'}
                ],
                value='erdos_renyi',
                style={'width': '50%', 'margin-bottom': '10px', 'font-size': '16px'}
            ),
        ], style={'margin-bottom': '20px'}),

        html.Div([
            html.Label('Graph Layout:', style={'font-weight': 'bold', 'font-size': '18px'}),
            dcc.Dropdown(
                id='dropdown-layout',
                options=[
                    {'label': 'Spring Layout', 'value': 'spring'},
                    {'label': 'Circular Layout', 'value': 'circular'},
                    {'label': 'Random Layout', 'value': 'random'},
                    {'label': 'Kamada-Kawai Layout', 'value': 'kamada_kawai'},
                    {'label': 'Fruchterman-Reingold Layout', 'value': 'fruchterman_reingold'}
                ],
                value='spring',
                style={'width': '50%', 'margin-bottom': '10px', 'font-size': '16px'}
            ),
        ], style={'margin-bottom': '20px'}),

        html.Div([
            html.Label('Number of Nodes:', style={'font-weight': 'bold', 'font-size': '18px'}),
            dcc.Input(
                id='input-num-nodes',
                type='number',
                value=20,
                min=2,
                max=100,
                step=1,
                style={'width': '10%', 'margin-right': '20px', 'font-size': '16px'}
            ),

            html.Label('Number of Edges:', style={'font-weight': 'bold', 'font-size': '18px'}),
            dcc.Input(
                id='input-num-edges',
                type='number',
                value=30,
                min=1,
                max=200,
                step=0.1,
                style={'width': '10%', 'margin-right': '20px', 'font-size': '16px'}
            ),
        ], style={'margin-bottom': '20px'}),

    ], className='container'),

    dcc.Graph(id='graph-visualization', style={'height': '70vh'}),
])

# Callback to update graph based on user input
@app.callback(
    Output('graph-visualization', 'figure'),
    [Input('dropdown-graph-type', 'value'),
     Input('input-num-nodes', 'value'),
     Input('input-num-edges', 'value'),
     Input('dropdown-layout', 'value')]
)
def update_graph(graph_type, num_nodes, num_edges, layout_algorithm):
    num_nodes = int(num_nodes)
    num_edges = float(num_edges)

    # Generate the random graph
    G = generate_random_graph(num_nodes, num_edges, graph_type)

    # Create positions for the nodes
    if layout_algorithm == 'spring':
        pos = nx.spring_layout(G)
    elif layout_algorithm == 'circular':
        pos = nx.circular_layout(G)
    elif layout_algorithm == 'random':
        pos = nx.random_layout(G)
    elif layout_algorithm == 'kamada_kawai':
        pos = nx.kamada_kawai_layout(G)
    elif layout_algorithm == 'fruchterman_reingold':
        pos = nx.fruchterman_reingold_layout(G)
    else:
        pos = nx.spring_layout(G)  # Default to Spring layout

    # Calculate degree centrality for coloring nodes
    node_degrees = nx.degree_centrality(G)
    node_colors = [node_degrees[node] for node in G.nodes()]

    # Plotly trace for edges
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Populate edge_trace with data from G
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    # Plotly trace for nodes
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=node_colors,  # Assign node colors based on degree centrality
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Attribute',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2)
        )
    )

    # Populate node_trace with data from G
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([f'Node {node}<br>Degree Centrality: {node_degrees[node]:.2f}'])

    # Create figure object
    figure = {
        'data': [edge_trace, node_trace],
        'layout': go.Layout(
            title='Graph Visualized',
            titlefont=dict(size=24, family='Arial, sans-serif', color='#007bff'),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='#f8f9fa',  # Background color
            paper_bgcolor='#f8f9fa'  # Background color
        )
    }

    return figure

# Main function to run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
