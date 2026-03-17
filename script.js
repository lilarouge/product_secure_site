document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addForm");
    const feedback = document.getElementById("feedback");

    console.log("JS loaded and DOM ready!");

    form.addEventListener("submit", async function (e) {
        e.preventDefault(); // prevent normal page reload

        const formData = new FormData(form);

        try {
            const response = await fetch("/add-product", {
                method: "POST",
                body: new URLSearchParams(formData)
            });

            const text = await response.text(); // server message

            if (response.status === 400) {
                // Error feedback (e.g., product exists or invalid)
                feedback.innerText = text;
                feedback.className = "error";
            } else {
                // Success feedback
                feedback.innerText = text;
                feedback.className = "success";
                form.reset();
            }

            console.log("Fetch response:", response.status, text);
        } catch (err) {
            feedback.innerText = "Error connecting to server.";
            feedback.style.color = "red";
            console.error(err);
        }
    });
});