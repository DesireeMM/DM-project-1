document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    
    const calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: { center: 'dayGridMonth,timeGridWeek' }, // buttons for switching between views
      
        views: {
          dayGridMonth: { // name of view
            titleFormat: { year: 'numeric', month: '2-digit', day: '2-digit' }
            // other view-specific options here
          }
        },
    });

    fetch('/api/events')
          .then((response) => response.json())
          .then((events) => {
            for (const event of events) {
              calendar.addEvent(event)
            }
            calendar.render();
        })
        
  });