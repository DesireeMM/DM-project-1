const leaveButtons = document.querySelectorAll('.leave-event');

for (const button of leaveButtons) {
    button.addEventListener('click', () => {
    
        const leaveResponse = confirm("Are you sure you cannot attend? This action is not reversible.")
    
        if (leaveResponse == true) {
            const eventID = button.id
        
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
}