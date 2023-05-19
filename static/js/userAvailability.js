document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    
    const calendar = new FullCalendar.Calendar(calendarEl, {
        timeZone: 'UTC',
      initialView: 'timeGridWeek',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'timeGridWeek,timeGridDay'
      },
    });
    const calendarButtons = document.querySelectorAll(".button");
    for (const button of calendarButtons) {
      button.classList.add("btn");
    }

    fetch('/api/user-availability')
          .then((response) => response.json())
          .then((availabilities) => {
            for (const availability of availabilities) {
              console.log(availability)
              calendar.addEvent(availability);
            }
          
            calendar.render();
        })
        
  });