document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("searchForm");
    const resultsDiv = document.getElementById("results");

    form.addEventListener("submit", async (e) => {
        e.preventDefault(); // Prevent full page reload

        const query = document.getElementById("query").value.trim();

        // Clear previous results
        resultsDiv.innerHTML = "";

        if (query === "") return;

        try {
            // Send GET request to /search?query=...
            const response = await fetch(`/search?query=${encodeURIComponent(query)}`);

            if (!response.ok) {
                resultsDiv.innerHTML = `<p style="color:red;">Error: ${await response.text()}</p>`;
                return;
            }

            const data = await response.json();

            if (data.length === 0) {
                resultsDiv.innerHTML = `<p>No products found.</p>`;
                return;
            }

            // Create a list of results
            const ul = document.createElement("ul");
            ul.style.listStyle = "none";
            ul.style.padding = "0";

            data.forEach(item => {
                const li = document.createElement("li");
                li.style.background = "#ffffff";
                li.style.padding = "10px";
                li.style.marginBottom = "10px";
                li.style.borderRadius = "8px";
                li.style.boxShadow = "0 2px 5px rgba(0,0,0,0.1)";
                li.textContent = `${item.name} - $${item.price}`;
                ul.appendChild(li);
            });

            resultsDiv.appendChild(ul);

        } catch (err) {
            console.error(err);
            resultsDiv.innerHTML = `<p style="color:red;">Error fetching results</p>`;
        }
    });
});