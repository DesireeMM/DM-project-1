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

    fetch('/api/user-availability')
          .then((response) => response.json())
          .then((events) => {
            for (const event of events) {
              calendar.addEvent(event)
              console.log(event);
            }
            calendar.render();
        })
        
  });