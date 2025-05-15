# Fama Barber Shop and Beauty Salon Website

A modern, responsive website for Fama Barber Shop and Beauty Salon built with Flask, HTML5, CSS3, and JavaScript.

## Features

- Responsive design optimized for all devices
- Dynamic service listing with pricing
- Online booking system
- Testimonials and review management
- Photo gallery with lightbox
- Contact form with Google Maps integration
- Admin dashboard for content management

## Tech Stack

- **Backend**: Python with Flask
- **Database**: SQLite (can be upgraded to PostgreSQL for production)
- **Frontend**: HTML5, CSS3, JavaScript, jQuery
- **Styling**: Custom CSS
- **Forms**: Flask-WTF
- **Authentication**: Flask-Login
- **Email**: Flask-Mail

## Requirements

- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone [repository_url]
cd [repository_directory]
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables for configuration:
- Create a `.env` file in the project root with the following:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=username
MAIL_PASSWORD=password
MAIL_USE_TLS=True
ADMIN_EMAIL=admin@example.com
```

5. Initialize the database:
```bash
flask run
```
The database will be created automatically on the first run.

## Usage

1. Start the application:
```bash
flask run
```

2. Access the website at: `http://localhost:5000`

3. Access the admin dashboard at: `http://localhost:5000/login`
   - Default admin credentials:
     - Username: admin
     - Password: adminpassword
   - *Important: Change the default password in production!*

## Project Structure

```
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── static/             # Static files (CSS, JS, images)
│   ├── css/            # CSS stylesheets
│   ├── js/             # JavaScript files
│   ├── img/            # Image assets
│   └── uploads/        # User uploaded content
├── templates/          # HTML templates
│   ├── admin/          # Admin dashboard templates
│   └── ...             # Frontend templates
└── instance/           # Instance-specific files
    └── barbershop.db   # SQLite database
```

## Admin Features

- Dashboard with statistics and quick access to recent items
- Manage services (add, edit, delete)
- View and manage appointments
- Upload and manage gallery images
- Moderate customer reviews
- Respond to contact messages

## Customization

- The website content can be modified through the admin dashboard
- For design changes, modify the CSS files in `static/css/`
- To change functionality, update the JavaScript files in `static/js/`
- For structural changes, edit the templates in `templates/`

## Deployment

For production deployment:

1. Update the SECRET_KEY in the .env file
2. Configure a proper mail server
3. Set FLASK_ENV=production
4. Consider upgrading to PostgreSQL for the database
5. Deploy using Gunicorn and Nginx (or a similar setup)
6. Set up SSL for secure connections

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Font Awesome](https://fontawesome.com/)
- [jQuery](https://jquery.com/)
- [AOS Animation Library](https://michalsnik.github.io/aos/) 