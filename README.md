# **Spotify Statistics Web Application**

<img width="1435" alt="image" src="https://github.com/user-attachments/assets/6b2d832a-ffe4-43b4-839b-fb6d86d26876">


## **Objective**
The goal of this project was to design and develop a Spotify listening statistics summary website, inspired by **Spotify Wrapped**, using **Django** and the **Spotify API**. Users can view personalized summaries of their music listening habits, save their wraps for future reference, and interact with the application via a sleek, responsive user interface.

---

## **Features**
### **Base Features**
1. **Spotify Listening Statistics Summary**
   - Users can generate a detailed and creative summary of their music listening habits and tastes.
   - The summary consists of at least 8 distinct slides showcasing:
     - Top tracks and artists.
     - Recently played songs.
     - Genres and total listening time.
   - Styled to resemble a fun and colorful presentation.

2. **User Authentication**
   - Integration with Spotify's OAuth system for login and user identification.
   - Persistent accounts that allow users to save and revisit their Spotify wraps.
   - Ability to log out and delete accounts.

3. **Spotify Wrap Management**
   - Users can save their Spotify wraps and access them later through a dedicated page.
   - Wraps can be viewed in detail and deleted individually if needed.

4. **Contact the Developers**
   - A fully functional contact form allows users to send feedback or suggestions to the development team.
   - Submissions are redirected to a "Thank You" page with an option to return to the homepage.
   - Email debugging is handled via Django's `console.EmailBackend`.

### **Advanced Features**
1. **Responsive UI**
   - The application is optimized for different screen resolutions, including mobile devices.
   - The UI dynamically adjusts to provide an aesthetically pleasing experience.

2. **Data Security**
   - API keys and other secrets are securely stored and excluded from the repository using `.gitignore`.

3. **Dynamic Descriptions**
   - Users can generate insights about their music taste using an LLM API.
   - Additional feature: Compare music tastes with friends for a Duo-Wrapped experience.

4. **Dark Mode**
   - Users can toggle between light and dark modes for the application UI.

5. **Multi-Language Support**
   - The UI supports English and at least two additional languages.

6. **Music Playback**
   - Users can listen to clips of their top tracks directly from the application.

---

## **Tech Stack**
- **Frontend**: HTML, CSS, JavaScript (Bootstrap for responsiveness)
- **Backend**: Django (Python)
- **APIs**: Spotify Web API, Groq API
- **Database**: SQLite (default Django database, easily configurable for PostgreSQL/MySQL)
- **Other Tools**: Django's Email Backend for debugging contact forms.

---
### **Hosted Site Link**
https://spotifywrapper.onrender.com/
---

### **Steps to Run Locally**

## **Setup and Installation**
### **Prerequisites**
- Python 3.10 or higher
- Spotify Developer Account
- Django installed (`pip install django`)
- Access to the LLM API (if implementing the description feature)
---

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd spotify_wrapped
   
2. Install dependencies:
   pip install -r requirements.txt

3. Set up your Spotify API keys:
Create an .env file in the project directory.
Add your Spotify Client ID and Secret:
Also add groq api key (very easy to get)
   CLIENT_ID=<your-client-id>
   CLIENT_SECRET=<your-client-secret>
   GROQ_API=<key>

4. Migrate the database:
  python manage.py makemigrations
   python manage.py migrate

5. Start the server:
  python manage.py runserver

6. Access the application:
  http://127.0.0.1:8000
---

### **Jira Page** 
https://chilukam04.atlassian.net/jira/software/projects/C2P2/summary


