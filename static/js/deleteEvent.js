const deleteButton = document.querySelector('#delete-event');

deleteButton.addEventListener('click', () => {

    const deleteResponse = confirm("Are you sure you want to delete this event? This action is not reversible.")

    if (deleteResponse == true) {
        const eventID = document.querySelector('#event_id_num').value
    
        const formInputs = {
            "event_id": eventID,
        }

        fetch('/delete-event', {
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