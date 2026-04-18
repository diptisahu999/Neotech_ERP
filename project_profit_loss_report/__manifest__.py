{
    'name': 'Project Profit & Loss Report',
    'version': '1.0',
    'description': """
        This module adds a profit and loss report for projects, 
        allowing users to analyze the financial performance of their projects.""",
    'depends': [
        'project', 
        'sale', 
        'account', 
        'stock', 
        'mrp', 
        'purchase'],
    'data': [
        'views/project_profit_views.xml',
        'views/project_profit_menu.xml',
    ],
    'installable': True,
}