document.addEventListener("DOMContentLoaded", function () {
    updateEventDetails();
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

function submitForm(event) {
    event.preventDefault();

    // Final validation to ensure correctness
    validatePeople();

    // Hide the form and show thank you message
    document.getElementById("registrationForm").style.display = "none";
    document.getElementById("thankYouMessage").style.display = "block";
    document.getElementById("overlay").style.display = "block";

    setTimeout(() => {
        window.location.href = "upevents.html";
    }, 3000);
}
