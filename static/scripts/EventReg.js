document.addEventListener("DOMContentLoaded", function () {
    updateEventDetails();
    
    const form = document.getElementById("registrationForm");
    if (form) {
        form.addEventListener("submit", submitForm);
    }
});

function updateEventDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const eventId = urlParams.get("event");

    const eventNames = {
        "event1": "Konkani Mai Bhas",
        "event2": "Konkani Food & Cultural Festival 2025",
        "event3": "Konkani Heritage & Literature Meet"
    };

    const eventNameElement = document.getElementById("eventName");
    const eventInputElement = document.getElementById("eventInput");

    if (eventId && eventNameElement && eventInputElement) {
        const eventName = eventNames[eventId] || "Unknown Event";
        eventNameElement.textContent = eventName;
        eventInputElement.value = eventName;
    }
}

function updateSubsections() {
    const totalPeople = parseInt(document.getElementById("people").value);
    const subsections = document.getElementById("subsections");

    if (totalPeople >= 1) {
        subsections.style.display = "block";
        document.getElementById("adults").max = totalPeople;
        document.getElementById("children").max = totalPeople;
    } else {
        subsections.style.display = "none";
    }
}

function validatePeople() {
    const totalPeople = parseInt(document.getElementById("people").value);
    let adults = parseInt(document.getElementById("adults").value) || 0;
    let children = parseInt(document.getElementById("children").value) || 0;

    if (adults > totalPeople) {
        document.getElementById("adults").value = totalPeople;
        adults = totalPeople;
    }

    if (children > totalPeople - adults) {
        document.getElementById("children").value = totalPeople - adults;
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const redirectBtn = document.getElementById("redirectBtn");
    if (redirectBtn) {
        redirectBtn.addEventListener("click", function () {
            window.location.href = "{{ url_for('home') }}";
        });
    }
});


function submitForm(event) {
    event.preventDefault();

    // Final validation to ensure correctness
    validatePeople();

    // Hide the form and show thank you message
    document.getElementById("registrationForm").style.display = "none";
    document.getElementById("thankYouMessage").style.display = "block";
    document.getElementById("overlay").style.display = "block";

    // Get home URL from the thankYouMessage div
    const homeUrl = document.getElementById("thankYouMessage").getAttribute("data-home-url");

    // Redirect to home after 3 seconds
    setTimeout(() => {
        window.location.href = homeUrl;
    }, 3000);
}


