async function loadRooms() {
    const response = await fetch("/rooms");
    const rooms = await response.json();
    const container = document.getElementById("rooms");
    container.innerHTML = rooms
        .map((room) => `<div class="room-card"><h2>Номер ${room.number}</h2><p>${room.room_type}, ${room.price_per_night} руб.</p></div>`)
        .join("");
}

document.addEventListener("DOMContentLoaded", loadRooms);
