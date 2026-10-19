
const csrfToken = document.querySelector(
    "[name=csrfmiddlewaretoken]"
).value;

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            ...(options.headers || {})
        },
        credentials: "same-origin"
    });

    let data = null;

    if (response.status !== 204) {
        data = await response.json().catch(() => null);
    }

    if (!response.ok) {
        const errors = data
            ? Object.values(data).flat().join("; ")
            : "Ошибка выполнения запроса";
        throw new Error(errors);
    }

    return data;
}

const categorySelect = document.getElementById("category");
const form = document.getElementById("ticket-form");
const titleInput = document.getElementById("title");
const message = document.getElementById("message");
const list = document.getElementById("tickets-list");
const loading = document.getElementById("loading");
const filter = document.getElementById("status-filter");

function showMessage(text, isError = false) {
    message.textContent = text;
    message.className = "alert " +
        (isError ? "alert-danger" : "alert-success");
}

async function loadCategories() {
    const categories = await apiRequest("/tickets/api/categories/");

    categorySelect.replaceChildren();

    for (const category of categories) {
        const option = document.createElement("option");
        option.value = category.id;
        option.textContent = category.name;
        categorySelect.append(option);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        await apiRequest("/tickets/api/tickets/", {
            method: "POST",
            body: JSON.stringify({
                title: titleInput.value,
                category: Number(categorySelect.value)
            })
        });

        titleInput.value = "";
        await loadTickets();
        showMessage("Заявка успешно создана");

    } catch (error) {
        showMessage("Ошибка: " + error.message, true);
    }
});

async function changeStatus(ticketId, newStatus) {
    await apiRequest(`/tickets/api/tickets/${ticketId}/`, {
        method: "PATCH",
        body: JSON.stringify({status: newStatus})
    });

    await loadTickets();
}

async function deleteTicket(ticketId, ticketTitle) {
    if (!confirm(`Удалить заявку «${ticketTitle}»?`)) {
        return false;
    }

    await apiRequest(`/tickets/api/tickets/${ticketId}/`, {
        method: "DELETE"
    });

    await loadTickets();
    return true;
}

async function loadTickets() {
    loading.hidden = false;

    const params = new URLSearchParams();

    if (filter.value) {
        params.set("status", filter.value);
    }

    const query = params.toString();
    const url = "/tickets/api/tickets/" +
        (query ? "?" + query : "");

    try {
        const tickets = await apiRequest(url);
        list.replaceChildren();

        if (tickets.length === 0) {
            const empty = document.createElement("p");
            empty.textContent = "Заявки не найдены";
            list.append(empty);
            return;
        }

        for (const ticket of tickets) {
            const row = document.createElement("div");
            row.className =
                "d-flex justify-content-between align-items-center border-bottom py-3 gap-3 flex-wrap";

            const title = document.createElement("div");
            title.textContent =
                ticket.title + " — " + ticket.category_name;

            const status = document.createElement("span");
            status.className = "badge bg-blue-lt";

            const statusNames = {
                new: "Новая",
                progress: "В работе",
                done: "Выполнена"
            };

            status.textContent = statusNames[ticket.status];

            const actions = document.createElement("div");
            actions.className = "d-flex gap-2";

            if (ticket.status !== "done") {
                const changeButton = document.createElement("button");
                changeButton.className = "btn btn-primary btn-sm";
                changeButton.textContent = "Изменить статус";

                changeButton.addEventListener("click", async () => {
                    const nextStatus = ticket.status === "new"
                        ? "progress" : "done";

                    changeButton.disabled = true;

                    try {
                        await changeStatus(ticket.id, nextStatus);
                        showMessage("Статус успешно изменён");
                    } catch (error) {
                        changeButton.disabled = false;
                        showMessage("Ошибка: " + error.message, true);
                    }
                });

                actions.append(changeButton);
            }

            const deleteButton = document.createElement("button");
            deleteButton.className = "btn btn-danger btn-sm";
            deleteButton.textContent = "Удалить";

            deleteButton.addEventListener("click", async () => {
                try {
                    const deleted = await deleteTicket(
                        ticket.id, ticket.title
                    );

                    if (deleted) {
                        showMessage("Заявка успешно удалена");
                    }
                } catch (error) {
                    showMessage("Ошибка: " + error.message, true);
                }
            });

            actions.append(deleteButton);
            row.append(title, status, actions);
            list.append(row);
        }

    } catch (error) {
        showMessage("Ошибка загрузки: " + error.message, true);
    } finally {
        loading.hidden = true;
    }
}

filter.addEventListener("change", loadTickets);

async function initialize() {
    try {
        await loadCategories();
        await loadTickets();
    } catch (error) {
        showMessage("Ошибка: " + error.message, true);
    }
}

initialize();

