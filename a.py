import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px

# Step 1: Load and Combine Data
file1_path = 'sheet_1.xlsx'


data1 = pd.read_excel(file1_path, sheet_name='Sheet1')


combined_data = pd.concat([data1 ], ignore_index=True)
combined_data['PO Document Date'] = pd.to_datetime(combined_data['PO Document Date'])

# Step 2: Define User Authentication Data
USER_CREDENTIALS = {'admin': 'password123'}

# Step 3: Initialize the Dash App
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Step 4: Define Login Page Layout
login_layout = html.Div([
    html.H1("Login to Dashboard", style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#FF6347'}),
    html.Div([
        html.Label("Username:", style={'fontSize': '18px', 'color': '#5D5D5D'}),
        dcc.Input(id='username', type='text', placeholder='Enter username', style={'width': '100%', 'padding': '10px', 'borderRadius': '8px'}),
        html.Br(),
        html.Br(),
        html.Label("Password:", style={'fontSize': '18px', 'color': '#5D5D5D'}),
        dcc.Input(id='password', type='password', placeholder='Enter password', style={'width': '100%', 'padding': '10px', 'borderRadius': '8px'}),
        html.Br(),
        html.Button('Login', id='login-button', n_clicks=0, style={'backgroundColor': '#4CAF50', 'color': 'white', 'width': '100%', 'padding': '10px', 'borderRadius': '8px', 'cursor': 'pointer'}),
    ], style={'width': '300px', 'margin': '0 auto'}),
    html.Div(id='login-message', style={'color': 'red', 'textAlign': 'center', 'marginTop': '20px'})
])

# Step 5: Define Dashboard Layout
dashboard_layout = html.Div([
    html.H1("Purchase Order Dashboard", style={'textAlign': 'center', 'fontSize': 36, 'color': '#1E90FF'}),

    html.Div([  # Buttons for different views
        html.Button('📊 Total PO Values', id='btn-total-po', n_clicks=0, style={'backgroundColor': '#FF6347', 'color': 'white', 'padding': '15px 32px', 'borderRadius': '8px', 'cursor': 'pointer'}),
        html.Button('🛒 Vendor Distribution', id='btn-vendor-dist', n_clicks=0, style={'backgroundColor': '#1E90FF', 'color': 'white', 'padding': '15px 32px', 'borderRadius': '8px', 'cursor': 'pointer'}),
        html.Button('📦 Purchase Groups', id='btn-purchase-groups', n_clicks=0, style={'backgroundColor': '#32CD32', 'color': 'white', 'padding': '15px 32px', 'borderRadius': '8px', 'cursor': 'pointer'}),
        html.Button('🏆 Top Vendors by Category', id='btn-top-vendors-category', n_clicks=0, style={'backgroundColor': '#FF4500', 'color': 'white', 'padding': '15px 32px', 'borderRadius': '8px', 'cursor': 'pointer'}),
        html.Button('📈 Rate Variations', id='btn-rate-variations', n_clicks=0, style={'backgroundColor': '#FFD700', 'color': 'black', 'padding': '15px 32px', 'borderRadius': '8px', 'cursor': 'pointer'}),
    ], style={'display': 'flex', 'justifyContent': 'center', 'gap': '20px', 'marginBottom': '30px'}),
    
    html.Div([  # Dropdown for Item Filtering
    html.Label("Filter by Item:", style={'fontSize': 18, 'color': '#1E90FF'}),
    dcc.Dropdown(
        id='item-filter',
        options=[{'label': item, 'value': item} for item in combined_data['Item Text'].unique()],
        placeholder="Select an Item",
        multi=False,
        style={'width': '50%', 'margin': '0 auto', 'borderRadius': '8px'}
    ),
], style={'textAlign': 'center', 'marginBottom': '30px'}),


    html.Div([  # Dropdown to filter by company
        html.Label("Filter by Company:", style={'fontSize': 18, 'color': '#1E90FF'}),
        dcc.Dropdown(
            id='company-filter',
            options=[{'label': comp, 'value': comp} for comp in combined_data['Comp Name'].unique()],
            placeholder="Select a Company",
            multi=True,
            style={'width': '50%', 'margin': '0 auto', 'borderRadius': '8px'}
        ),
    ], style={'textAlign': 'center', 'marginBottom': '30px'}),

    html.Div([  # Date range picker
        html.Label("Select Date Range:", style={'fontSize': 18, 'color': '#1E90FF'}),
        dcc.DatePickerRange(
            id='date-range-picker',
            start_date=combined_data['PO Document Date'].min().date(),
            end_date=combined_data['PO Document Date'].max().date(),
            display_format='YYYY-MM-DD',
            style={'width': '50%', 'margin': '0 auto', 'borderRadius': '8px'}
        ),
    ], style={'textAlign': 'center', 'marginBottom': '30px'}),

    html.Div(id='content-container', style={'padding': '20px'}),
])

# Step 6: Define Layout for Application with Navigation
app.layout = html.Div([  # Main layout with navigation between pages
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    [Output('login-message', 'children'),
     Output('url', 'pathname')],
    [Input('login-button', 'n_clicks')],
    [State('username', 'value'),
     State('password', 'value')]
)
def login(n_clicks, username, password):
    if n_clicks > 0:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            return "", "/dashboard"
        else:
            return "Invalid username or password. Please try again.", dash.no_update
    return "", dash.no_update

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/dashboard':
        return dashboard_layout
    else:
        return login_layout
@app.callback(
    Output('content-container', 'children'),
    [Input('btn-total-po', 'n_clicks'),
     Input('btn-vendor-dist', 'n_clicks'),
     Input('btn-purchase-groups', 'n_clicks'),
     Input('btn-top-vendors-category', 'n_clicks'),
     Input('btn-rate-variations', 'n_clicks')],
    [Input('company-filter', 'value'),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('item-filter', 'value')]
)
def update_content(btn_po, btn_vendor, btn_purchase, btn_top_vendors, btn_rate_variations, selected_companies, start_date, end_date, selected_item):
    filtered_data = combined_data
    if selected_companies:
        selected_companies = [comp.strip() for comp in selected_companies]
        filtered_data = filtered_data[filtered_data['Comp Name'].str.strip().isin(selected_companies)]

    # Filter data by selected date range
    if start_date and end_date:
        filtered_data = filtered_data[ 
            (filtered_data['PO Document Date'] >= pd.to_datetime(start_date)) & 
            (filtered_data['PO Document Date'] <= pd.to_datetime(end_date)) 
        ]
    if selected_item:
        filtered_data = filtered_data[filtered_data['Item Text'] == selected_item]


    # Determine which button triggered the callback
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'btn-total-po'
    
    # Colorful charts and updates based on the selected button
    

  
    if button_id == 'btn-top-vendors-category':
        category_vendor_data = filtered_data.groupby(['CATEGORY', 'Vendor Name']).agg(
        Total_PO_Value=('Total PO Value in CR', 'sum'),
        PO_Count=('PO Number', 'count')
    ).reset_index()

    # Sort by CATEGORY and Total_PO_Value for top vendors
        top_vendors_by_category = category_vendor_data.sort_values(
        by=['CATEGORY', 'Total_PO_Value'], ascending=[True, False]
    ).groupby('CATEGORY').head(1)

    # Sort the result by CATEGORY in ascending order for the table
        top_vendors_by_category = top_vendors_by_category.sort_values(by='CATEGORY')

    # Create bar chart
        bar_fig = px.bar(
        top_vendors_by_category,
        x='CATEGORY',
        y='Total_PO_Value',
        color='Vendor Name',
        title='Top Vendors by Category',
        text='Total_PO_Value',
        template='plotly_dark',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={'Total_PO_Value': 'Total PO Value (CR)', 'CATEGORY': 'Category'}
    )

    # Create DataTable
        table = dash.dash_table.DataTable(
        data=top_vendors_by_category.to_dict('records'),
        columns=[
            {'name': 'CATEGORY', 'id': 'CATEGORY'},
            {'name': 'Vendor Name', 'id': 'Vendor Name'},
            {'name': 'Total_PO_Value', 'id': 'Total_PO_Value'},
            {'name': 'PO_Count', 'id': 'PO_Count'}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={'backgroundColor': '#1E90FF', 'color': 'white'}
    )

        return html.Div([
        html.H3("Top Vendors by Category", style={'textAlign': 'center', 'marginBottom': '20px', 'color': '#FF6347'}),
        dcc.Graph(figure=bar_fig, style={'height': '60vh'}),
        html.Div(table, style={'padding': '20px'})
    ])




    elif button_id == 'btn-vendor-dist':
        # Vendor frequency and dependency analysis
        vendor_analysis = filtered_data.groupby('Vendor Name').agg(
            Total_PO_Value=('Total PO Value in CR', 'sum'),
            PO_Count=('PO Number', 'count')
        ).reset_index()

        # Highlight top vendors by Total PO Value
        top_vendors_value = vendor_analysis.nlargest(10, 'Total_PO_Value')

        # Bar chart for Top Vendors by PO Value
        bar_fig_value = px.bar(
            top_vendors_value, 
            x='Vendor Name', 
            y='Total_PO_Value',
            title='Top 10 Vendors by PO Value',
            text='Total_PO_Value',
            labels={'Total_PO_Value': 'Total PO Value (CR)'},
            template='plotly_white'
        )

        # Highlight top vendors by PO Count
        top_vendors_count = vendor_analysis.nlargest(10, 'PO_Count')

        # Bar chart for Top Vendors by PO Count
        bar_fig_count = px.bar(
            top_vendors_count, 
            x='Vendor Name', 
            y='PO_Count',
            title='Top 10 Vendors by PO Count',
            text='PO_Count',
            labels={'PO_Count': 'PO Count'},
            template='plotly_white'
        )

        # Display Vendor Summary
        vendor_summary = html.Div([
            html.H3("Vendor Performance Overview", style={'textAlign': 'center'}),
            html.P(f"Total Vendors: {vendor_analysis.shape[0]}", style={'textAlign': 'center'}),
            html.P(f"Top Vendor by PO Value: {top_vendors_value.iloc[0]['Vendor Name']} "
                   f"({top_vendors_value.iloc[0]['Total_PO_Value']:.2f} CR)", style={'textAlign': 'center'}),
            html.P(f"Top Vendor by PO Count: {top_vendors_count.iloc[0]['Vendor Name']} "
                   f"({top_vendors_count.iloc[0]['PO_Count']} POs)", style={'textAlign': 'center'})
        ], style={'marginBottom': '20px'})

        return html.Div([
            vendor_summary,
            dcc.Graph(figure=bar_fig_value, style={'height': '50vh'}),
            dcc.Graph(figure=bar_fig_count, style={'height': '50vh'})
        ])

    elif button_id == 'btn-total-po':
        # Line chart for total PO values
        total_po = filtered_data.groupby('PO Document Date')['Total PO Value in CR'].sum().reset_index()
        main_fig = px.line(total_po, x='PO Document Date', y='Total PO Value in CR',
                           title='Total PO Value Over Time', markers=True, template='plotly_dark')

        # Pie chart for PO vs Non-PO values
        po_non_po_data = filtered_data['Category'].value_counts().reset_index()
        po_non_po_data.columns = ['Category', 'Count']
        po_pie_fig = px.pie(po_non_po_data, names='Category', values='Count',
                            title='Category Distribution', color_discrete_sequence=px.colors.qualitative.Pastel)
        
        # Calculate max and min PO values
        max_po_value = total_po['Total PO Value in CR'].max()
        min_po_value = total_po['Total PO Value in CR'].min()

        # Display max and min PO values
        po_value_summary = html.Div([
            html.H3(f"Maximum PO Value: {max_po_value:.2f} CR", style={'textAlign': 'center'}),
            html.H3(f"Minimum PO Value: {min_po_value:.2f} CR", style={'textAlign': 'center'}),
        ], style={'textAlign': 'center', 'marginBottom': '20px'})

        return html.Div([
            po_value_summary,
            dcc.Graph(figure=main_fig, style={'height': '50vh'}),
            dcc.Graph(figure=po_pie_fig, style={'height': '40vh'})
        ])

    elif button_id == 'btn-purchase-groups':
        # Bar chart for purchase group distribution
        purchase_dist = filtered_data['Purchase Group'].value_counts().reset_index()
        purchase_dist.columns = ['Purchase Group', 'Count']
        main_fig = px.bar(purchase_dist, x='Purchase Group', y='Count', title='Purchase Group Distribution',
                          text='Count', template='plotly_white')

        return dcc.Graph(figure=main_fig, style={'height': '60vh'})
    elif button_id == 'btn-rate-variations':
    # Filter by selected item
        if 'item-filter' in ctx.inputs and ctx.inputs['item-filter.value']:
            selected_item = ctx.inputs['item-filter.value']
        filtered_data = filtered_data[filtered_data['Item Text'] == selected_item]

    # If no data is available, return a message
    if filtered_data.empty:
        return html.Div([
            html.H3(f"No data found for the selected item.", style={'textAlign': 'center', 'color': 'red'}),
        ])

    # Identify top 10 vendors for the selected item
    top_vendors = (
        filtered_data.groupby('Vendor Name')['Rate']
        .sum()
        .nlargest(10)  # Top 10 vendors by total rate
        .index
    )

    # Filter data to include only these top 10 vendors
    filtered_data = filtered_data[filtered_data['Vendor Name'].isin(top_vendors)]

    # Prepare data for rate variation graph
    rate_data = filtered_data[['PO Document Date', 'Rate', 'Vendor Name', 'Item Text']].dropna()
    rate_data = rate_data.groupby(['PO Document Date', 'Vendor Name']).agg({'Rate': 'mean'}).reset_index()

    # Create the rate variation graph
    rate_graph = px.line(
        rate_data,
        x='PO Document Date',
        y='Rate',
        color='Vendor Name',
        title=f'Rate Variations Over Time for "{selected_item}"' if selected_item else 'Rate Variations Over Time',
        labels={'Rate': 'Average Rate', 'PO Document Date': 'Date', 'Vendor Name': 'Vendor'},
        template='plotly_dark',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # Return the graph
    return dcc.Graph(figure=rate_graph)

    
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080, dev_tools_ui=False, dev_tools_props_check=False)