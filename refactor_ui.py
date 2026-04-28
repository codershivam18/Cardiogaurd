import os
import re

template_dir = r"d:\imp\Heart Disease Predictor\templates"

new_head_content = """    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Google Font -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <!-- Premium CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
</head>"""

new_nav = """    <!-- Global Premium Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark px-4 sticky-top">
        <a class="navbar-brand text-white" href="{{ url_for('home') }}">❤️ CardioGuard</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('symptoms') }}">Symptoms</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('prediction_page') }}">New Prediction</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('contacts') }}">Top Doctors</a>
                </li>
                {% if session.get('user_id') %}
                <li class="nav-item">
                    <a class="nav-link text-warning fw-bold" href="{{ url_for('dashboard') }}">Dashboard</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link text-danger fw-bold" href="{{ url_for('logout') }}">Logout</a>
                </li>
                {% else %}
                <li class="nav-item">
                    <a class="nav-link fw-bold" href="{{ url_for('login') }}">Login</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link text-info fw-bold" href="{{ url_for('register') }}">Register</a>
                </li>
                {% endif %}
            </ul>
        </div>
    </nav>
    
    <!-- Flash Messages Global Container -->
    <div class="container mt-3">
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }} alert-dismissible fade show shadow-sm" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}
    </div>"""

def refactor_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace everything from the first <style> to </style> and </head> with the new link to main.css
    # We use regex to handle varying styles.
    # Some files might have multiple links, but we'll try to just target the style block and </head>
    
    # 1. Remove inline <style>...</style>
    content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
    
    # 2. Inject CSS link right before </head>
    content = re.sub(r'</head>', f'    <link rel="stylesheet" href="{{{{ url_for(\'static\', filename=\'css/main.css\') }}}}">\n</head>', content)
    
    # 3. Replace <nav>...</nav> block with new dynamic nav.
    # Note: Some files don't have nav (like predict.html initially, though we might want to add it).
    # We'll just replace existing navs.
    if '<nav' in content:
        content = re.sub(r'<nav.*?</nav>', new_nav, content, flags=re.DOTALL)
    else:
        # inject nav after <body>
        content = re.sub(r'<body>', f'<body>\n{new_nav}', content, flags=re.DOTALL)

    # 4. For forms/cards, add glass-card wrapper if applicable. Instead of complex regex, 
    # we'll do massive replacements for known classes.
    content = content.replace('class="form-card"', 'class="glass-card"')
    content = content.replace('class="login-card"', 'class="glass-card"')
    content = content.replace('class="result-card text-center"', 'class="glass-card text-center"')
    content = content.replace('class="info-card text-center"', 'class="glass-card text-center"')
    content = content.replace('class="symptom-card text-center"', 'class="glass-card text-center"')
    content = content.replace('class="doctor-card text-center"', 'class="glass-card text-center"')
    
    content = content.replace('class="btn text-center mt-4"', 'class="text-center mt-4"')
    content = content.replace('class="btn btn-primary-custom mt-4"', 'class="btn btn-premium mt-4"')
    content = content.replace('class="btn btn-predict w-100"', 'class="btn btn-premium w-100"')
    content = content.replace('class="btn btn-custom"', 'class="btn btn-premium"')
    content = content.replace('class="btn btn-custom w-100"', 'class="btn btn-premium w-100"')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
for file in os.listdir(template_dir):
    if file.endswith('.html'):
        refactor_file(os.path.join(template_dir, file))

print("Refactoring complete.")
