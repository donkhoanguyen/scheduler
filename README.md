# ai_scheduler

system/
├── backend/
│   ├── api_integration/
│   │   ├── calendar_api.py       # Interacts with api_1
│   │   ├── email_api.py          # Interacts with api_2
│   │   ├── ai_agent.py           # AI logic for summarizing, suggesting, scheduling
│   │   └── scheduler.py          # Handles time slot checks and scheduling logic
│   ├── routes.py                 # Backend API endpoints (user approval, suggestions)
│   └── config.py                 # API keys, secrets, etc.
├── frontend/                     # User-facing app (web or mobile)
│   ├── components/
│   │   ├── CalendarView.js       # Calendar interface
│   │   ├── SuggestionsView.js    # Show suggested meetings
│   ├── App.js                    # Main frontend logic
│   └── api.js                    # Calls backend endpoints
├── tests/
│   ├── test_calendar_api.py
│   ├── test_email_api.py
│   ├── test_ai_agent.py
│   └── test_scheduler.py
└── README.md