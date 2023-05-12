const leaveButtons = document.querySelectorAll('.leave-group');

for (const button of leaveButtons) {
    button.addEventListener('click', () => {
    
        const leaveResponse = confirm("Are you sure you want to leave this group? This action is not reversible.")
    
        if (leaveResponse == true) {
            const groupID = button.id
        
            const formInputs = {
                "group_id": groupID,
            }
    
            fetch('/leave-group', {
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