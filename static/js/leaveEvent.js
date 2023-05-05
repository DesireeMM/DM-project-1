const leaveButton = document.querySelector('#leave-event');

leaveButton.addEventListener('click', () => {

    const leaveResponse = confirm("Are you sure you cannot attend? This action is not reversible.")

    if (leaveResponse == true) {
        const eventID = document.querySelector('#leave-event').value
    
        const formInputs = {
            "event_id": eventID,
        }

        fetch('/leave-event', {
            method: 'POST',
            body: JSON.stringify(formInputs),
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(responseJson => {
            alert(responseJson.status);
            window.location.replace(responseJson.redirect);
        })
    }
})