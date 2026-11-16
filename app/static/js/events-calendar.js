(() => {
    const monthTitle = document.querySelector("#calendar-month");
    const grid = document.querySelector("#calendar-grid");
    const agendaDate = document.querySelector("#agenda-date");
    const agendaEvents = document.querySelector("#agenda-events");
    const errorMessage = document.querySelector("#calendar-error");
    const searchInput = document.querySelector("#calendar-search-input");
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    let displayedMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    let selectedDate = new Date(today);
    let events = [];
    let searchQuery = "";

    const dateKey = (date) => [
        date.getFullYear(),
        String(date.getMonth() + 1).padStart(2, "0"),
        String(date.getDate()).padStart(2, "0"),
    ].join("-");

    const monthLabel = new Intl.DateTimeFormat("ru-RU", {
        month: "long",
        year: "numeric",
    });

    const readableDate = new Intl.DateTimeFormat("ru-RU", {
        day: "numeric",
        month: "long",
        year: "numeric",
    });

    const eventTime = (event) => {
        if (event.all_day) return "Весь день";
        const time = event.starts_at.slice(11, 16);
        return time || "Весь день";
    };

    const filteredEvents = () => {
        const query = searchQuery.trim().toLocaleLowerCase("ru");
        return events.filter((event) => (
            !query
            || event.title.toLocaleLowerCase("ru").includes(query)
            || (event.location || "").toLocaleLowerCase("ru").includes(query)
        ));
    };

    const eventsOnDate = (date) => {
        const key = dateKey(date);
        return filteredEvents().filter((event) => {
            const firstDay = event.starts_at.slice(0, 10);
            const lastDay = (event.ends_at || event.starts_at).slice(0, 10);
            return key >= firstDay && key <= lastDay;
        });
    };

    const renderAgenda = () => {
        agendaDate.textContent = readableDate.format(selectedDate);
        agendaEvents.replaceChildren();
        const dayEvents = eventsOnDate(selectedDate);

        if (!dayEvents.length) {
            const empty = document.createElement("p");
            empty.className = "agenda-empty";
            empty.textContent = searchQuery
                ? "Ничего не найдено."
                : "На этот день мероприятий нет.";
            agendaEvents.append(empty);
            return;
        }

        dayEvents.forEach((event) => {
            const card = document.createElement("article");
            card.className = "agenda-event";

            const time = document.createElement("span");
            time.className = "agenda-event-time";
            time.textContent = eventTime(event);
            card.append(time);

            const title = document.createElement("h4");
            title.textContent = event.title;
            card.append(title);

            if (event.location) {
                const location = document.createElement("p");
                location.className = "agenda-event-location";
                location.textContent = event.location;
                card.append(location);
            }

            if (event.description) {
                const description = document.createElement("p");
                description.className = "agenda-event-description";
                description.textContent = event.description;
                card.append(description);
            }

            agendaEvents.append(card);
        });
    };

    const renderGrid = () => {
        monthTitle.textContent = monthLabel.format(displayedMonth);
        grid.replaceChildren();

        const firstOfMonth = new Date(displayedMonth);
        const start = new Date(firstOfMonth);
        start.setDate(firstOfMonth.getDate() - ((firstOfMonth.getDay() + 6) % 7));

        for (let index = 0; index < 42; index += 1) {
            const date = new Date(start);
            date.setDate(start.getDate() + index);
            const key = dateKey(date);
            const dayEvents = eventsOnDate(date);
            const cell = document.createElement("button");
            cell.type = "button";
            cell.className = "calendar-day";
            cell.setAttribute("role", "gridcell");
            cell.setAttribute("aria-label", `${readableDate.format(date)}, мероприятий: ${dayEvents.length}`);

            if (date.getMonth() !== displayedMonth.getMonth()) cell.classList.add("is-outside-month");
            if (key === dateKey(today)) cell.classList.add("is-today");
            if (key === dateKey(selectedDate)) cell.classList.add("is-selected");
            cell.addEventListener("click", () => {
                selectedDate = date;
                if (date.getMonth() !== displayedMonth.getMonth()) {
                    displayedMonth = new Date(date.getFullYear(), date.getMonth(), 1);
                    loadMonth();
                } else {
                    renderGrid();
                    renderAgenda();
                }
            });

            const number = document.createElement("span");
            number.className = "calendar-day-number";
            number.textContent = String(date.getDate());
            cell.append(number);

            const list = document.createElement("span");
            list.className = "calendar-day-events";
            dayEvents.slice(0, 2).forEach((event) => {
                const item = document.createElement("span");
                item.className = "calendar-event-chip";
                item.textContent = event.title;
                list.append(item);
            });
            if (dayEvents.length > 2) {
                const more = document.createElement("span");
                more.className = "calendar-event-more";
                more.textContent = `+ ещё ${dayEvents.length - 2}`;
                list.append(more);
            }
            cell.append(list);
            grid.append(cell);
        }

        renderAgenda();
    };

    const loadMonth = async () => {
        errorMessage.hidden = true;
        grid.setAttribute("aria-busy", "true");
        const month = `${displayedMonth.getFullYear()}-${String(displayedMonth.getMonth() + 1).padStart(2, "0")}-01`;
        try {
            const response = await fetch(`/events/data?month=${month}`);
            if (!response.ok) throw new Error(`Calendar request failed: ${response.status}`);
            events = await response.json();
            renderGrid();
        } catch (error) {
            console.error("Не удалось загрузить календарь мероприятий", error);
            events = [];
            renderGrid();
            errorMessage.hidden = false;
        } finally {
            grid.removeAttribute("aria-busy");
        }
    };

    document.querySelector("#calendar-previous").addEventListener("click", () => {
        displayedMonth = new Date(displayedMonth.getFullYear(), displayedMonth.getMonth() - 1, 1);
        loadMonth();
    });
    document.querySelector("#calendar-next").addEventListener("click", () => {
        displayedMonth = new Date(displayedMonth.getFullYear(), displayedMonth.getMonth() + 1, 1);
        loadMonth();
    });
    document.querySelector("#calendar-today").addEventListener("click", () => {
        displayedMonth = new Date(today.getFullYear(), today.getMonth(), 1);
        selectedDate = new Date(today);
        loadMonth();
    });
    searchInput.addEventListener("input", () => {
        searchQuery = searchInput.value;
        renderGrid();
    });

    loadMonth();
})();
