document.addEventListener('DOMContentLoaded', () => {
    const searchBar = document.getElementById('search-bar');
    const resultsContainer = document.getElementById('results');

    let debounceTimeout = null;

    searchBar.addEventListener('input', () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(async () => {
            const query = searchBar.value.trim();
            if (query.length > 0) {
                const response = await fetch(`/search?q=${query}`);
                const data = await response.json();
                displayResults(data.results);
            } else {
                resultsContainer.innerHTML = '';
                resultsContainer.style.display = 'none';
            }
        }, 300);  // Adjust the debounce delay as needed
    });

    function displayResults(results) {
        resultsContainer.innerHTML = '';
        if (results.length > 0) {
            resultsContainer.style.display = 'block';
            results.slice(0, 10).forEach(movie => {
                const linkElement = document.createElement('a');
                linkElement.href = `/movie/${movie.id}`;

                const moviePoster = movie.poster_path ? `https://image.tmdb.org/t/p/w200${movie.poster_path}` : 'https://via.placeholder.com/50x75';
                const movieTitle = movie.title || 'Untitled';
                const movieYear = movie.release_date ? movie.release_date.split('-')[0] : 'Unknown';

                linkElement.innerHTML = `
                    <div class="movie">
                    <img src="${moviePoster}" alt="${movieTitle}">
                        <p class="movie-title">${movieTitle}</p>
                        <p class="movie-year">${movieYear}</p>
                    </div>
                `;

                resultsContainer.appendChild(linkElement);
            });
        } else {
            resultsContainer.style.display = 'none';
        }
    }
});


document.addEventListener("DOMContentLoaded", async () => {
    const movieId = window.location.pathname.split("/").pop();
    try {
        const response = await fetch(`/api?q=${movieId}`);
        const data = await response.json();

        let genre = data.genres.map(genre => genre.name).join(', ');

        document.getElementById("movie-poster").src = data.poster_path ? `https://image.tmdb.org/t/p/w500${data.poster_path}` : 'https://via.placeholder.com/150x200';
        document.getElementById("movie-title").textContent = `${data.original_title || "Untitled"} (${data.release_date.split('-')[0]})`;
        document.getElementById("movie-info").textContent = `${data.release_date} • ${genre} • ${data.runtime}m`;
        document.getElementById("movie-score").textContent = `${(data.vote_average * 10).toFixed(0)}%`;
        document.getElementById("movie-synopsis").textContent = data.overview;
        document.getElementById("movie-tagline").textContent = data.tagline;
        document.getElementsByTagName("title")[0].innerHTML = `${data.original_title || "Untitled"} (${data.release_date.split('-')[0]})`;
        document.getElementById("imdb-link").href = `https://www.imdb.com/title/${data.imdb_id}`;
        if (data.backdrop_path){
            const movieContainer = document.getElementById("movie-container");
            movieContainer.style.backgroundImage = `url('https://image.tmdb.org/t/p/w1280${data.backdrop_path}')`;
            movieContainer.style.backgroundSize = 'cover';
            movieContainer.style.backgroundPosition = 'center';
        }
        
        for (let i = 0; i < data.videos.results.length; i++) {
            if (data.videos.results[i].type === 'Trailer' && data.videos.results[i].site === 'YouTube') {
                const trailerContainer = document.getElementById("trailer-container");
                const iframe = document.createElement("iframe");
                iframe.src = `https://www.youtube.com/embed/${data.videos.results[i].key}`;
                iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
                iframe.allowFullscreen = true;
                trailerContainer.appendChild(iframe);
                break;
            }
        }

        document.getElementById("watchlist-button").addEventListener("click", async () => {
            const response = await fetch(`/change/${movieId}/watchlist`);
            const status = await response.text();
            if (status === 'Added to watchlist'){
                document.getElementById("watchlist-button").textContent = "✓";
                document.getElementById("watchlist-button").title = "Added to Watchlist";
            }
            else if (status === 'Deleted'){
                document.getElementById("watchlist-button").textContent = "+";
                document.getElementById("watchlist-button").title = "Add to Watchlist";
            }
        });

        document.getElementById("watched-button").addEventListener("click", async () => {
            const response = await fetch(`/change/${movieId}/watched`);
            const status = await response.text();
            if (status === 'Added to watched'){
                document.getElementById("watched-button").textContent = "Watched"
                document.getElementById("watched-button").title = "Watched";
            }
            else if (status === 'Deleted'){
                document.getElementById("watched-button").textContent = "Mark Watched"
                document.getElementById("watched-button").title = "Mark Watched";
            }
            else if (status === 'Watched from watchlist'){
                document.getElementById("watched-button").textContent = "Watched"
                document.getElementById("watched-button").title = "Watched";
                document.getElementById("watchlist-button").textContent = "+";
                document.getElementById("watchlist-button").title = "Add to Watchlist";
            }
        });
    } catch (error) {
        console.error('Error fetching movie data:', error);
    }
});

