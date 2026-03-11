<div align="center">

# 🚨 RappiSafe

### Real-Time Safety Platform for Delivery Workers

[![Live Demo](https://img.shields.io/badge/demo-live-success?style=for-the-badge)](https://rappisafe-mdo8.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![WebSockets](https://img.shields.io/badge/WebSockets-Real--Time-orange?style=for-the-badge)](https://channels.readthedocs.io/)

**[Live Demo](https://rappisafe-mdo8.onrender.com/)** • **[Technical Documentation](FUNCIONAMIENTO.md)**

</div>

---

## 📖 About The Project

RappiSafe is a comprehensive real-time safety monitoring system designed to protect delivery workers during their routes. The platform provides instant emergency response, live GPS tracking, and centralized monitoring through a responsive web application.

**Key Impact:**
- ⚡ **Sub-5 second** emergency alert delivery
- 🗺️ **Real-time GPS tracking** updated every 5 seconds during emergencies
- 👥 **Centralized monitoring** dashboard for security operators
- 📱 **Mobile-first** responsive design for delivery workers

---

## 🎯 Core Features

### For Delivery Workers
- **3-Second Panic Button**: Long-press activation prevents accidental triggers
- **Automatic Location Sharing**: GPS coordinates sent every 5 seconds during active alerts
- **Emergency Contacts**: Manage up to 3 trusted contacts for automatic notifications
- **Psychological Support Requests**: Confidential channel for professional assistance
- **Battery Monitoring**: Real-time device battery tracking

### For Security Operators
- **Real-Time Dashboard**: WebSocket-powered instant alert notifications (<5s)
- **Interactive Maps**: Live tracking with route history using Leaflet.js
- **Incident Management**: Complete case tracking with action logs and timestamps
- **Multi-Alert Handling**: Simultaneous monitoring of multiple emergency situations
- **Emergency Contact Access**: Quick access to delivery worker's trusted contacts

### For Administrators
- **User Management**: Complete CRUD operations with role-based access control
- **Advanced Analytics**: Reports by time period, alert type, and geographic zones
- **Risk Zone Mapping**: Identification of high-incident areas
- **System Monitoring**: Django admin panel for full database access

---

## 🛠️ Technologies & Architecture

### Backend
- **Django 5.2.8** - Web framework with custom user authentication
- **Django Channels 4.0** - WebSocket implementation for real-time communication
- **Daphne** - ASGI server for WebSocket support
- **SQLite / PostgreSQL** - Database (production-ready for both)

### Frontend
- **Django Templates** - Server-side rendering
- **TailwindCSS** - Utility-first CSS framework (#dc2626 theme)
- **Vanilla JavaScript** - No dependencies, optimized performance
- **Leaflet.js** - Interactive mapping library

### Real-Time Features
- **WebSockets** - Bidirectional real-time communication
- **Geolocation API** - Device GPS access
- **Notifications API** - Browser push notifications
- **Battery API** - Device battery monitoring
- **Motion Detection** - Accelerometer/gyroscope ready for future implementation

### DevOps & Deployment
- **Render** - Cloud deployment platform
- **WhiteNoise** - Static file serving
- **Git** - Version control
- **Environment Variables** - Secure configuration management

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.10+
Node.js 18+
Git
```

### Installation

```bash
# Clone repository
git clone https://github.com/YaxcheItz/RAPPI-SAFE.git
cd RappiSafe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install

# Setup database
python manage.py migrate

# Compile CSS
npm run build:css

# Create superuser
python manage.py createsuperuser

# Run server (with WebSocket support)
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
```

Visit: **http://localhost:8000**

---

## 💻 System Architecture

```
┌─────────────────┐         WebSocket          ┌──────────────────┐
│  Delivery App   │◄──────────────────────────►│  Operator        │
│  (Mobile)       │      <5s latency           │  Dashboard       │
└────────┬────────┘                            └────────┬─────────┘
         │                                              │
         │ GPS Every 5s                                 │ WebSocket
         │                                              │
         └──────────────┬───────────────────────────────┘
                        │
                   ┌────▼──────┐
                   │  Django   │
                   │  Channels │
                   │  Consumer │
                   └────┬──────┘
                        │
              ┌─────────┴──────────┐
              │                    │
         ┌────▼─────┐        ┌────▼────┐
         │ Database │        │  Redis  │
         │ (SQLite) │        │ (Async) │
         └──────────┘        └─────────┘
```

---

## 📊 Key Technical Implementations

### Real-Time Communication
- **WebSocket Consumer** handles alert broadcasting to all active operators
- **Async task processing** ensures non-blocking operations
- **Channel layers** enable inter-process communication

### Security & Authentication
- **Role-based access control** (Delivery Worker, Operator, Administrator)
- **CSRF protection** on all forms
- **Secure password hashing** using Django's authentication system
- **Session management** with 24-hour expiration

### Database Design
- **Custom User model** extending AbstractUser with roles
- **UUID primary keys** for alerts (better security, distributed systems ready)
- **Optimized queries** with select_related and prefetch_related
- **Index on frequently queried fields** (status, created_at)

### API & Data Flow
- **RESTful principles** for data exchange
- **JSON responses** for AJAX requests
- **Geolocation validation** with precision tracking
- **Battery level monitoring** with low-battery alerts

---

## 🎨 UI/UX Highlights

- **Mobile-First Design**: Optimized for smartphones with large touch targets
- **Color-Coded Alerts**: Visual hierarchy with red (#dc2626) for emergencies
- **Progressive Enhancement**: Core functionality works without JavaScript
- **Accessibility**: WCAG 2.1 compliant semantic HTML
- **Responsive Layout**: Seamless experience across all devices

---

## 📈 Performance & Scalability

- **Sub-5 second** alert delivery time
- **Optimized WebSocket connections** with automatic reconnection
- **Efficient GPS batching** reduces server load
- **Static asset caching** with WhiteNoise
- **Database query optimization** using Django ORM best practices

**Scalability Considerations:**
- Ready for Redis Channel Layer for horizontal scaling
- PostgreSQL support for production workloads
- Stateless design enables load balancing
- CDN-ready static assets

---

## 🔒 Security Features

✅ HTTPS enforcement in production
✅ CSRF token validation
✅ SQL injection protection (Django ORM)
✅ XSS prevention (template auto-escaping)
✅ Secure password storage (PBKDF2)
✅ Role-based authorization
✅ Sensitive data encryption ready

---

## 🌐 Live Demo

**Application:** [https://rappisafe-mdo8.onrender.com/](https://rappisafe-mdo8.onrender.com/)

### 🔑 Test Credentials

| Role | Username | Password |
|------|----------|----------|
| **Administrator** | `admin` | `admin123` |
| **Delivery Driver** | `repartidor1` | `test123` |
| **Operator** | `operador1` | `test123` |

*Note: You can also use `repartidor2`, `repartidor3`, `operador2`, or `admin1` with the same password (`test123`).*

**Note:** First load may take 30-60 seconds due to free tier cold start.

---

## 📁 Project Structure

```
RappiSafe/
├── mysite/              # Django project configuration
│   ├── settings.py      # Project settings
│   ├── asgi.py          # ASGI application for WebSockets
│   └── urls.py          # Main URL routing
├── rappiSafe/           # Main application
│   ├── models.py        # Data models (User, Alert, Trajectory, etc.)
│   ├── views.py         # View controllers
│   ├── consumers.py     # WebSocket consumers
│   ├── routing.py       # WebSocket routing
│   └── templates/       # HTML templates
├── static/              # Static assets (CSS, JS, images)
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies
└── build.sh             # Deployment script
```

---

## 🚀 Deployment

This project is production-ready and deployed on **Render**. Key configuration:

- **Web Service** with Daphne ASGI server
- **Auto-deploy** from GitHub main branch
- **Environment variables** for sensitive configuration
- **Static file serving** via WhiteNoise
- **Health checks** for uptime monitoring

**Environment Variables:**
```bash
DEBUG=False
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=<optional-postgresql-url>
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[FUNCIONAMIENTO.md](FUNCIONAMIENTO.md)** | Complete technical documentation: architecture, data flow, code examples |
| **README.md** | This file - Project overview for recruiters and developers |

---

## 💡 Future Enhancements

- [ ] Automatic accident detection using device accelerometer
- [ ] Safe route calculation vs. fastest route
- [ ] Offline mode with Service Workers
- [ ] PDF report generation
- [ ] SMS notifications to emergency contacts
- [ ] Progressive Web App (PWA) with install prompt
- [ ] Integration with mapping APIs for route optimization
- [ ] Advanced analytics dashboard with Chart.js

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👤 Author

**Developer Portfolio Project**

- GitHub: [@YaxcheItz](https://github.com/YaxcheItz)
- Live Demo: [rappisafe-mdo8.onrender.com](https://rappisafe-mdo8.onrender.com/)

---

## 🙏 Acknowledgments

- **Django** - Robust web framework
- **Django Channels** - WebSocket support
- **TailwindCSS** - Modern CSS framework
- **Leaflet.js** - Interactive mapping
- **Render** - Deployment platform

---

<div align="center">

**⭐ Star this repo if you find it interesting!**

Made with ❤️ and ☕

[⬆ Back to Top](#-rappisafe)

</div>
