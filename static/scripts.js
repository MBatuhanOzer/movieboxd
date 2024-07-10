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
