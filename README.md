
# CrowdCares - Crowdfunding Platform

CrowdCares is a web-based crowdfunding platform built using Python Django that enables creative individuals, NGOs, and project owners to raise funds while giving investors a secure and transparent way to contribute.
The platform includes a role-based access system, project approval workflow, and real-time investment tracking—ensuring trust, quality, and accountability.

## Tech Stack

**Backend:** Python-Django

**Frontend:** HTML, CSS

**Database:** SQLite
## Run Locally

Clone the project

```bash
  git clone https://github.com/shaktisankpal/CrowdCares.git
```

Go to the project directory

```bash
  cd CrowdCares
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Apply Migrations
```bash
  python manage.py migrate
```

Run Server
```bash
  python manage.py runserver
```

Run Server
```bash
  http://127.0.0.1:8000/
```
## Features

### 🔐 Role-Based User Access

- **Investors**
  - Browse projects
  - Invest in campaigns
  - Track contributions

- **Project Creators / NGOs**
  - Create fundraising projects
  - Manage project details and updates

- **Administrators**
  - Approve or reject projects
  - Monitor platform activity

---

### 📝 Admin Approval Workflow

- All submitted projects go through an admin verification process  
- Ensures:
  - Quality control
  - Legitimacy of campaigns
  - Overall platform integrity

---

### 💰 Secure Investment Tracking

- Real-time dashboard to track funding progress  
- Transparent fund allocation records  
- Detailed contribution logs for each project

---

### 📊 Project Progress Monitoring

- Visual progress indicators showing percentage of funds raised  
- Live updates accessible to:
  - Project creators
  - Investors
