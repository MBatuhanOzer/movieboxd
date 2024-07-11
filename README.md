# MovieBoxd

#### Video Demo:  (https://youtu.be/YPZlqAqGRfA)

#### Description:

MovieBoxd is a web application designed to enhance your movie-watching experience. Whether you're a casual movie watcher or a dedicated cinephile, MovieBoxd provides a platform to search for movies, add them to your watchlist or watched list, and keep track of what you've seen and what you plan to watch next. The application leverages The Movie Database (TMDb) API to fetch movie details, ensuring you have access to a vast library of films.

### Features

1. **User Registration and Authentication**
   - Before accessing the main features of MovieBoxd, users are required to register and log in. This ensures that each user's data is kept private and secure.
   - The registration form is designed with Bootstrap for a responsive and visually appealing interface. It includes fields for username, password, and password confirmation.
   - After registration, users can log in using their credentials. The login process is secure and ensures that only registered users can access their personalized movie lists.

2. **Movie Search**
   - Once logged in, users can search for movies using the search bar. The search functionality is powered by the TMDb API, which provides detailed information about a wide range of movies.
   - Each movie in the search results includes essential details such as the title, release date.
   - Users can easily scroll through the search results to find the movies they're interested in.

3. **Watchlist and Watched List**
   - MovieBoxd allows users to organize their movie-watching plans with two main lists: Watchlist and Watched List.
   - Users can add movies to their Watchlist if they plan to watch them in the future. This helps users keep track of movies they want to see.
   - Once a movie has been watched, users can move it to the Watched List. This feature helps users keep a record of the movies they've seen.
   - Both lists are displayed in an organized manner, making it easy for users to manage their movie collections.

4. **Conditional Rendering with Jinja Templating**
   - The application uses Jinja templating to conditionally render HTML buttons for adding movies to the Watchlist or Watched List. This ensures that the buttons are displayed correctly based on the movie's status (whether it's already in the Watchlist or Watched List).

5. **Responsive Design**
   - MovieBoxd is designed to be responsive and works well on various devices, including desktops, tablets, and smartphones. The use of Bootstrap ensures that the layout adjusts smoothly to different screen sizes.
   - The navigation bar includes elements such as Films, Watchlist, Watched, and Logout, providing easy access to different sections of the application.

### Technical Details

1. **Backend**
   - The backend of MovieBoxd is built using Flask, a lightweight and flexible web framework for Python. Flask handles user authentication, movie searches, and database interactions.
   - The application requires a TMDb API key, which should be stored in a file named `api.txt` in the root directory. The API key should be placed on the first line of this file.

2. **Frontend**
   - The frontend of MovieBoxd is built using HTML, CSS, and Bootstrap. The combination of these technologies ensures a clean, modern, and user-friendly interface.
   - The search bar and results section are designed to be wide, providing ample space for displaying movie details.

3. **Database**
   - MovieBoxd uses a SQLite database to store user information and movie lists. This lightweight database is suitable for the application's requirements and is easy to set up and maintain.
   - The database schema includes tables for users, watchlist, and watched movies, ensuring efficient data management.

4. **Deployment**
   - To deploy MovieBoxd, you need to set up a Flask environment and install the required dependencies listed in the `requirements.txt` file.
   - The application can be run locally or deployed to a web server for online access.

### Installation and Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MBatuhanOzer/movieboxd.git
   cd movieboxd
2. Set Up the Virtual Environment

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
3. Install Dependencies

    ```bash
    pip install -r requirements.txt

4. Add TMDb API Key

    Create a file named api.txt in the root directory of the project.
    Add your TMDb API key to the first line of this file.
    Initialize the Database
5. Initialize the Database
    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
6. Run the Application

    ```bash
    flask run
7. Access the Application

    Open your web browser and go to http://127.0.0.1:5000.


Conclusion
MovieBoxd is a comprehensive movie management web application that allows users to search for movies, create watchlists, and keep track of watched movies. With a focus on user experience and responsive design, MovieBoxd is an excellent tool for movie enthusiasts. The application leverages modern web technologies and follows best practices in web development, making it a robust and reliable platform for managing your movie-watching activities.
